"""Tests for the per-label database splitter (`ytclip split-db`).

Splitting must be lossless (every window lands in exactly one shard) and must
keep a label entirely in its own file, so a single action can be loaded without
reading the whole multi-megabyte database.

Run with:  PYTHONPATH=src python -m pytest tests/ -q
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import ytclip.database as db


def _write_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def _row(vid, label, keep=1, is_step=1):
    # only the fields the splitter / writers touch need to be present
    return {c: "" for c in db.WINDOW_FIELDS} | {
        "video_id": vid, "action_label": label, "keep": keep, "is_step": is_step,
        "window_index": 0,
    }


def _setup(tmp_path, full, clean):
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    _write_jsonl(db_dir / "classifications.jsonl", full)
    _write_jsonl(db_dir / "classifications_clean.jsonl", clean)
    db.DB_DIR = str(db_dir)
    db.BY_LABEL_DIR = str(db_dir / "by_label")
    return db_dir


def test_split_is_lossless_and_grouped(tmp_path):
    full = ([_row("a", "talking_head", keep=0)] * 3
            + [_row("a", "pour_wax")] * 2
            + [_row("b", "melt_wax")])
    clean = [_row("a", "pour_wax")] * 2 + [_row("b", "melt_wax")]
    db_dir = _setup(tmp_path, full, clean)

    res = db.split_by_label()
    assert res["total_rows"] == 6 and res["total_clean_rows"] == 3
    assert res["labels"] == {"talking_head": 3, "pour_wax": 2, "melt_wax": 1}

    # lossless: shards sum back to the monolith
    by_label = db_dir / "by_label"
    total = sum(sum(1 for _ in open(by_label / f"{lbl}.jsonl"))
                for lbl in res["labels"])
    assert total == len(full)

    # each shard holds exactly one label
    for lbl in res["labels"]:
        rows = [json.loads(x) for x in open(by_label / f"{lbl}.jsonl")]
        assert {r["action_label"] for r in rows} == {lbl}


def test_split_writes_manifest_and_clean_shards(tmp_path):
    full = [_row("a", "talking_head", keep=0)] + [_row("a", "pour_wax")]
    clean = [_row("a", "pour_wax")]
    db_dir = _setup(tmp_path, full, clean)

    db.split_by_label()
    manifest = json.load(open(db_dir / "by_label" / "index.json"))
    assert manifest["total_rows"] == 2 and manifest["n_labels"] == 2
    assert manifest["labels"]["talking_head"]["clean_rows"] == 0
    assert manifest["labels"]["pour_wax"]["clean_rows"] == 1
    # clean shards live under by_label/clean/ and exclude filtered labels
    assert (db_dir / "by_label" / "clean" / "pour_wax.jsonl").exists()
    assert not (db_dir / "by_label" / "clean" / "talking_head.jsonl").exists()


def test_split_requires_built_db(tmp_path):
    db.DB_DIR = str(tmp_path / "empty")
    db.BY_LABEL_DIR = str(tmp_path / "empty" / "by_label")
    os.makedirs(db.DB_DIR)
    try:
        db.split_by_label()
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass
