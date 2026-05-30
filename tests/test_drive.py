"""Tests for the Drive sync bridge (push-set selection, base64 decode, newest-wins import)."""
import base64
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ytclip import drive, shared_db


def _seed(root, vid, niche="candles"):
    rows = [{"video_id": vid, "window_index": 0, "start_s": 0.0, "end_s": 8.0,
             "action_label": "pour_wax", "is_step": 1, "keep": 1, "filter_reason": "",
             "video_title": f"t{vid}", "video_url": f"u/{vid}", "video_duration_s": 50.0,
             "source": "storyboard"}]
    shared_db.ingest_rows(vid, rows, meta={"niche": niche}, root=root)


def test_records_to_push_skips_remote(tmp_path):
    root = str(tmp_path)
    _seed(root, "a"); _seed(root, "b")
    plan = drive.records_to_push(["a.json.gz"], root=root)   # 'a' already on Drive
    assert [r["title"] for r in plan] == ["b.json.gz"]
    assert drive.records_to_push([], root=root)[0]["title"] == "a.json.gz"


def test_decode_matches_download_content(tmp_path):
    root = str(tmp_path)
    _seed(root, "a")
    text = drive.record_text("a", root=root)
    # emulate download_file_content for a plain upload: base64 of the file bytes
    content = base64.b64encode(text.encode()).decode()
    assert drive.decode(content) == text
    assert json.loads(drive.decode(content))["video_id"] == "a"


def test_gzip_upload_round_trip(tmp_path):
    """record_gz_b64 -> (download) -> decode must reproduce the record exactly."""
    root = str(tmp_path)
    _seed(root, "a")
    payload = drive.record_gz_b64("a", root=root)        # what we'd upload as base64Content
    # what download_file_content returns is the same base64 of the stored gz bytes
    text = drive.decode(payload)
    assert json.loads(text)["video_id"] == "a"
    assert text == drive.record_text("a", root=root)
    # gzip is much smaller than raw
    assert len(base64.b64decode(payload)) < len(drive.record_text("a", root=root))


def test_import_downloaded_newest_wins(tmp_path):
    src, dst = str(tmp_path / "s"), str(tmp_path / "d")
    _seed(src, "a")
    text = drive.record_text("a", root=src)

    r1 = drive.import_downloaded([{"text": text}], root=dst)
    assert (r1["added"], r1["updated"], r1["skipped"], r1["bad"]) == (1, 0, 0, 0)
    # same record again -> skipped (not newer)
    r2 = drive.import_downloaded([{"text": text}], root=dst)
    assert (r2["added"], r2["updated"], r2["skipped"], r2["bad"]) == (0, 0, 1, 0)
    # newer record via base64 content path -> updated
    rec = json.loads(text); rec["ingested_at"] = "2099-01-01T00:00:00Z"; rec["video_title"] = "new"
    content = base64.b64encode(json.dumps(rec).encode()).decode()
    r3 = drive.import_downloaded([{"content": content}], root=dst)
    assert (r3["added"], r3["updated"], r3["skipped"], r3["bad"]) == (0, 1, 0, 0)
    assert shared_db.load_record("a", dst)["video_title"] == "new"


def test_import_skips_corrupt_payloads(tmp_path):
    """A garbled/truncated download must be skipped, never poison the store."""
    root = str(tmp_path)
    _seed(root, "good_src" if False else "a")           # one good record (as text)
    good = drive.record_text("a", root=root)
    res = drive.import_downloaded([
        {"text": good},                                 # valid
        {"content": "!!!not base64!!!"},                # garbage
        {"content": base64.b64encode(b"\x1f\x8btruncated-gzip").decode()},  # bad gzip
        {"text": "{not json"},                          # invalid json
    ], root=str(tmp_path / "dst"))
    assert res["added"] == 1 and res["bad"] == 3


def test_import_dir_rebuilds(tmp_path):
    src, dst = str(tmp_path / "s"), str(tmp_path / "d")
    _seed(src, "a"); _seed(src, "b")
    res = drive.import_dir(os.path.join(src, "records"), root=dst)
    assert res["added"] == 2 and res["rebuilt"] == 2
    assert os.path.exists(os.path.join(dst, "index.json"))
