"""Tests for the concurrency-safe, Drive-syncable shared clip store.

The store keeps one self-contained record per video (records/<id>.json) as the
source of truth, so many chats can ingest at once without clobbering each other,
the same video is never double-counted, and talking-head / on-screen-text windows
are flagged out of the usable-footage set.

Run with:  PYTHONPATH=src python -m pytest tests/ -q
"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ytclip import shared_db


def _row(vid, w, label, is_step=1, keep=1, filter_reason=""):
    return {"video_id": vid, "window_index": w, "start_s": w * 8.0,
            "end_s": w * 8.0 + 8, "action_label": label, "is_step": is_step,
            "keep": keep, "filter_reason": filter_reason,
            "video_title": f"title {vid}", "video_url": f"u/{vid}",
            "video_duration_s": 100.0, "source": "storyboard"}


def _video(vid, niche="candles"):
    # 2 action windows + 1 talking head + 1 text-overlay window
    rows = [_row(vid, 0, "pour_wax"), _row(vid, 1, "melt_wax"),
            _row(vid, 2, "talking_head", is_step=0, keep=0, filter_reason="talking_head"),
            _row(vid, 3, "decorate_finish", keep=0, filter_reason="text_overlay")]
    return rows, {"niche": niche}


def test_ingest_writes_record_with_flags(tmp_path):
    root = str(tmp_path)
    rows, meta = _video("vidA")
    res = shared_db.ingest_rows("vidA", rows, meta=meta, root=root)
    assert res["n_windows"] == 4 and res["n_usable"] == 2 and res["n_flagged"] == 2

    assert os.path.exists(shared_db.record_path("vidA", root))
    rec = shared_db.load_record("vidA", root)
    assert rec["niche"] == "candles" and len(rec["windows"]) == 4
    # talking-head and text-overlay windows are flagged
    flagged = {f["window_index"]: f["reason"] for f in shared_db.flagged_windows("vidA", root)}
    assert flagged == {2: "talking_head", 3: "text_overlay"}
    assert shared_db.is_flagged("vidA", 2, root) and not shared_db.is_flagged("vidA", 0, root)
    assert shared_db.is_ingested("vidA", root)


def test_usable_clips_excludes_flagged(tmp_path):
    root = str(tmp_path)
    rows, meta = _video("vidA")
    shared_db.ingest_rows("vidA", rows, meta=meta, root=root)
    clips = shared_db.usable_clips(root=root)
    labels = sorted(c["action_label"] for c in clips)
    assert labels == ["melt_wax", "pour_wax"]      # no talking_head, no text-overlay window
    assert shared_db.usable_clips(niche="candles", root=root)
    assert shared_db.usable_clips(niche="soap", root=root) == []


def test_ingest_is_idempotent(tmp_path):
    root = str(tmp_path)
    rows, meta = _video("vidA")
    shared_db.ingest_rows("vidA", rows, meta=meta, root=root)
    again = shared_db.ingest_rows("vidA", rows, meta=meta, root=root)
    assert again["skipped"] is True
    forced = shared_db.ingest_rows("vidA", rows, meta=meta, root=root, force=True)
    assert forced["skipped"] is False


def test_concurrent_ingest_of_distinct_videos_is_lossless(tmp_path):
    root = str(tmp_path)
    ids = [f"vid{i:03d}" for i in range(40)]

    def work(vid):
        rows, meta = _video(vid)
        return shared_db.ingest_rows(vid, rows, meta=meta, root=root)

    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(work, ids))

    m = shared_db.rebuild_views(root)
    assert m["videos"] == 40
    assert m["windows"] == 40 * 4
    assert m["usable"] == 40 * 2 and m["flagged"] == 40 * 2
    # materialized view for an action label has exactly one entry per video
    pour = [json.loads(l) for l in open(os.path.join(root, "by_label", "pour_wax.jsonl"))]
    assert len(pour) == 40 and len({r["video_id"] for r in pour}) == 40


def test_rebuild_views_manifest(tmp_path):
    root = str(tmp_path)
    for vid in ("a", "b"):
        rows, meta = _video(vid)
        shared_db.ingest_rows(vid, rows, meta=meta, root=root)
    m = shared_db.rebuild_views(root)
    assert m["videos"] == 2 and m["niches"] == ["candles"]
    assert m["labels"]["pour_wax"] == 2          # one pour_wax window per video
    assert json.load(open(os.path.join(root, "index.json")))["video_ids"] == ["a", "b"]


def test_rebuild_writes_one_csv_per_label(tmp_path):
    import csv
    root = str(tmp_path)
    for vid in ("a", "b"):
        rows, meta = _video(vid)
        shared_db.ingest_rows(vid, rows, meta=meta, root=root)
    shared_db.rebuild_views(root)
    # a .csv beside every .jsonl, with a header + the right number of rows
    cp = os.path.join(root, "by_label", "pour_wax.csv")
    assert os.path.exists(cp) and os.path.exists(os.path.join(root, "by_label", "pour_wax.jsonl"))
    rows = list(csv.DictReader(open(cp)))
    assert len(rows) == 2 and rows[0]["action_label"] == "pour_wax"
    assert "description_detailed" in rows[0] and "window_url" in rows[0]


def test_import_record_round_trip_newest_wins(tmp_path):
    """Simulate pulling another chat's record down from Drive."""
    src, dst = str(tmp_path / "src"), str(tmp_path / "dst")
    rows, meta = _video("vidA")
    shared_db.ingest_rows("vidA", rows, meta=meta, root=src)
    text = open(shared_db.record_path("vidA", src)).read()

    # first import lands; re-import of same (not newer) is skipped
    assert shared_db.import_record(text, root=dst)["skipped"] is False
    assert shared_db.is_ingested("vidA", dst)
    assert shared_db.import_record(text, root=dst)["skipped"] is True

    # a strictly newer record wins
    rec = json.loads(text)
    rec["ingested_at"] = "2099-01-01T00:00:00Z"
    rec["video_title"] = "updated"
    assert shared_db.import_record(json.dumps(rec), root=dst)["skipped"] is False
    assert shared_db.load_record("vidA", dst)["video_title"] == "updated"
