"""Tests for coverage / pending (read-first) and shotlist building (footage selection)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ytclip import select, shared_db


def _row(vid, w, label, conf=0.8, dur=8.0, is_step=1, keep=1, filter_reason=""):
    return {"video_id": vid, "window_index": w, "start_s": w * 8.0,
            "end_s": w * 8.0 + dur, "duration_s": dur, "action_label": label,
            "is_step": is_step, "keep": keep, "filter_reason": filter_reason,
            "confidence": conf, "description": f"{label} clip", "description_detailed": f"{label} detail",
            "window_url": f"https://youtu.be/{vid}?t={w*8}s",
            "video_title": f"title {vid}", "video_url": f"u/{vid}",
            "video_duration_s": 100.0, "source": "storyboard"}


def _ingest(root, vid, niche="candles", confs=(0.9, 0.5)):
    rows = [_row(vid, 0, "melt_wax", conf=confs[0]), _row(vid, 1, "pour_wax", conf=confs[1]),
            _row(vid, 2, "talking_head", is_step=0, keep=0, filter_reason="talking_head")]
    shared_db.ingest_rows(vid, rows, meta={"niche": niche}, root=root)


def test_coverage_groups_by_niche(tmp_path):
    root = str(tmp_path)
    _ingest(root, "a", niche="candles")
    _ingest(root, "b", niche="soap")
    cov = shared_db.coverage(root)
    assert cov["videos"] == 2
    assert set(cov["niches"]) == {"candles", "soap"}
    # talking_head is not an action label, so not counted as usable footage
    assert "talking_head" not in cov["usable_by_label"]
    assert cov["usable_by_label"]["melt_wax"] == 2


def test_pending_skips_already_ingested_and_parses_urls(tmp_path):
    root = str(tmp_path)
    _ingest(root, "havevid0001")
    res = shared_db.pending([
        "havevid0001",                                   # bare id, already in store
        "https://www.youtube.com/watch?v=newvid00002",   # url, new
        "https://youtu.be/newvid00002",                  # dup of the above
        "https://youtu.be/havevid0001?t=30s",            # url form of the one we have
    ], root)
    assert res["pending"] == ["newvid00002"]
    assert res["covered"] == ["havevid0001"]


def test_shotlist_orders_steps_excludes_flagged_and_ranks(tmp_path):
    root = str(tmp_path)
    # two videos; melt_wax confidences differ so ranking is observable
    _ingest(root, "a", confs=(0.9, 0.4))
    _ingest(root, "b", confs=(0.6, 0.7))
    order = ["melt_wax", "pour_wax", "talking_head"]      # talking_head must yield nothing
    sl = select.build_shotlist(niche="candles", order=order, per_step=2, root=root)

    steps = {s["label"]: s for s in sl["steps"]}
    assert steps["talking_head"]["clips"] == []          # flagged label excluded
    # melt_wax ranked by confidence: video a (0.9) before b (0.6)
    assert [c["video_id"] for c in steps["melt_wax"]["clips"]] == ["a", "b"]
    # max_per_video default 1 -> at most one clip per video per step
    assert len(steps["melt_wax"]["clips"]) == 2
    md = select.render_markdown(sl)
    assert "Shotlist" in md and "talking-head" in md


def test_write_shotlist_persists(tmp_path, monkeypatch):
    root = str(tmp_path / "store")
    _ingest(root, "a")
    monkeypatch.setattr(select, "SHOTLIST_DIR", str(tmp_path / "shotlists"))
    sl = select.write_shotlist(niche="candles", order=["melt_wax"], root=root)
    assert os.path.exists(sl["_paths"]["json"]) and os.path.exists(sl["_paths"]["md"])
