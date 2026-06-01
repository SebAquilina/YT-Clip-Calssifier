"""Minimal invariant tests: window bounds, rules smoothing, taxonomy validity.

Run with:  PYTHONPATH=src python -m pytest tests/ -q
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ytclip.rules import refine, merge_adjacent
from ytclip.segment import Window, windows_from_shots
from ytclip.taxonomy import load_rules, load_taxonomy


def test_windows_never_exceed_max():
    rules = load_rules()
    cap = rules["windowing"]["max_seconds"]
    # one long shot + one tiny shot
    wins = windows_from_shots([(0, 47), (47, 49)], duration=49, rules=rules)
    assert wins, "expected windows"
    assert all(w.duration <= cap + 1e-6 for w in wins)


def test_taxonomy_loads_and_has_steps():
    tax = load_taxonomy()
    assert tax.step_ids, "expected at least one procedure step"
    # canonical_order labels must all exist in the taxonomy
    rules = load_rules()
    for lbl in rules["canonical_order"]:
        assert lbl in tax.labels, f"{lbl} missing from taxonomy"


def test_despike_fixes_isolated_misread():
    tax = load_taxonomy()
    wins = [Window(i, i * 8, i * 8 + 8) for i in range(3)]
    raw = [
        {"label": "melt_wax", "confidence": 0.8, "evidence": ""},
        {"label": "pour_wax", "confidence": 0.5, "evidence": ""},   # isolated spike
        {"label": "melt_wax", "confidence": 0.8, "evidence": ""},
    ]
    out = refine(wins, raw, tax)
    assert out[1]["label"] == "melt_wax"
    assert out[1]["smoothed"] is True


def test_merge_adjacent_collapses_runs():
    refined = [
        {"window": 0, "start": 0, "end": 8, "label": "melt_wax", "phase": "process",
         "is_step": True, "confidence": 0.8},
        {"window": 1, "start": 8, "end": 16, "label": "melt_wax", "phase": "process",
         "is_step": True, "confidence": 0.6},
        {"window": 2, "start": 16, "end": 24, "label": "pour_wax", "phase": "assemble",
         "is_step": True, "confidence": 0.7},
    ]
    segs = merge_adjacent(refined)
    assert len(segs) == 2
    assert segs[0]["label"] == "melt_wax" and segs[0]["end"] == 16
