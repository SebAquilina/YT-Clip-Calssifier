"""Tests for grounded description enrichment (`ytclip enrich-db`).

Enrichment must (a) always produce >50 chars, (b) only add clauses derived from
signals we actually have, and (c) never quote the raw, often-garbled OCR text.

Run with:  PYTHONPATH=src python -m pytest tests/ -q
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import ytclip.enrich as enrich


def _row(**kw):
    base = dict(description="", action_label="pour_wax", phase="assemble",
                start_s=42.0, end_s=50.0, duration_s=8.0, video_duration_s=600.0,
                motion=0.27, brightness=0.56, colorfulness=0.1,
                dominant_colors="#d6b9a2,#675d3b", has_caption=0, ocr_text="")
    base.update(kw)
    return base


def test_enrichment_is_over_50_chars_even_for_terse_input():
    out = enrich.enrich_description(_row(description="", action_label="talking_head",
                                         phase="aux"))
    assert len(out) > 50


def test_generic_description_gets_canonical_gloss():
    out = enrich.enrich_description(_row(description="Host talks to camera.",
                                         action_label="talking_head", phase="aux"))
    # the taxonomy gloss for talking_head mentions "no hands-on action"
    assert "no hands-on action" in out
    assert out.startswith("Host talks to camera.")


def test_specific_description_is_preserved_as_lead():
    desc = "Stream of cream wax poured from a metal pitcher into an amber jar."
    out = enrich.enrich_description(_row(description=desc))
    assert out.startswith(desc.rstrip("."))


def test_visual_and_timing_clauses_are_grounded():
    out = enrich.enrich_description(_row(motion=0.0, brightness=0.05,
                                         dominant_colors="#000000,#030102"))
    assert "static shot" in out and "dark" in out
    assert "#000000" in out          # palette is verifiable (hex included)
    assert "assemble phase" in out and "0:42–0:50" in out
    assert "~7% in" in out            # 42/600


def test_raw_ocr_is_never_quoted():
    garbled = "yee ba it 1 PRBS SISCe ESOS In ie be PAR"
    out = enrich.enrich_description(_row(has_caption=1, ocr_text=garbled))
    assert "PRBS" not in out and "SISCe" not in out
    assert "captioned" in out         # we surface the reliable flag instead


def test_color_naming_is_deterministic():
    assert enrich._name_color("#000000") == "black"
    assert enrich._name_color("#ffffff") == "white"
    assert enrich._name_color("#bad") is None     # malformed -> no name


def _write_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def test_enrich_db_backfills_column(tmp_path):
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    rows = [_row(description="Host talks to camera.", action_label="talking_head",
                 phase="aux", motion=0.02)]
    _write_jsonl(db_dir / "classifications.jsonl", rows)
    _write_jsonl(db_dir / "classifications_clean.jsonl", [])
    enrich.DB_DIR = str(db_dir)

    res = enrich.enrich_db()
    assert res["rows"] == 1 and res["over_50"] == 1 and res["min_len"] > 50
    out = json.loads((db_dir / "classifications.jsonl").read_text())
    assert "description_detailed" in out and len(out["description_detailed"]) > 50
    # csv mirror is written with the new column
    assert "description_detailed" in (db_dir / "classifications.csv").read_text().splitlines()[0]


def test_enrich_db_requires_built_db(tmp_path):
    enrich.DB_DIR = str(tmp_path / "nope")
    os.makedirs(enrich.DB_DIR)
    try:
        enrich.enrich_db()
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass
