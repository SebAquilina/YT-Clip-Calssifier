"""Rules engine: turn raw per-window vision labels into a cleaned timeline.

Operations (all configured in config/rules.yaml):
  * despike    - replace an isolated single-window label whose identical
                 neighbours disagree with it (likely a misread)
  * fill_gaps  - fill a low-confidence window whose neighbours agree
  * backward-jump annotation - flag implausible reversals of canonical order
                 (unless the pair is listed as `repeatable`)

Input  : windows (with .index/.start/.end) + raw labels list aligned by index,
         each {label, confidence, evidence}
Output : list of RefinedLabel dicts with final label + audit notes.
"""
from __future__ import annotations

from typing import Dict, List

from .taxonomy import Taxonomy, load_rules


def _repeatable_set(rules: dict) -> set:
    return {frozenset(p) for p in rules.get("repeatable", [])}


def _canon_index(rules: dict) -> Dict[str, int]:
    return {lbl: i for i, lbl in enumerate(rules["canonical_order"])}


def refine(windows, raw: List[dict], tax: Taxonomy, rules: dict | None = None) -> List[dict]:
    rules = rules or load_rules()
    sm = rules["smoothing"]
    conf = rules["confidence"]
    aux = set(conf["aux_labels"])
    canon = _canon_index(rules)
    repeatable = _repeatable_set(rules)

    n = len(windows)
    labels = [dict(r) for r in raw]          # shallow copy
    for i, r in enumerate(labels):
        r.setdefault("confidence", 0.6)
        r.setdefault("evidence", "")
        # detailed free-text description of what happens in the window; fall back
        # to the short evidence string if a caller only provided that.
        r.setdefault("description", r.get("evidence", ""))
        r["original_label"] = r["label"]
        r["notes"] = []

    def neighbours_agree(i):
        if 0 < i < n - 1:
            return labels[i - 1]["label"] == labels[i + 1]["label"]
        return False

    # 1) despike isolated single-window disagreements
    if sm.get("despike"):
        for i in range(1, n - 1):
            cur = labels[i]
            if (cur["label"] != labels[i - 1]["label"]
                    and neighbours_agree(i)
                    and cur["confidence"] < 0.8):
                cur["label"] = labels[i - 1]["label"]
                cur["notes"].append("despiked to match neighbours")

    # 2) fill low-confidence gaps where neighbours agree
    if sm.get("fill_gaps"):
        thr = sm.get("gap_confidence_below", 0.55)
        for i in range(1, n - 1):
            cur = labels[i]
            if cur["confidence"] < thr and neighbours_agree(i) and cur["label"] != labels[i - 1]["label"]:
                cur["label"] = labels[i - 1]["label"]
                cur["notes"].append("gap-filled from neighbours")

    # 3) annotate backward jumps through canonical order
    last_step_idx = -1
    for i in range(n):
        lbl = labels[i]["label"]
        if lbl in aux or lbl not in canon:
            continue
        ci = canon[lbl]
        if last_step_idx >= 0 and ci < last_step_idx:
            prev = rules["canonical_order"][last_step_idx]
            if frozenset({lbl, prev}) not in repeatable:
                labels[i]["notes"].append(
                    f"backward step vs canonical order ({prev}->{lbl})")
        last_step_idx = max(last_step_idx, ci)

    # finalise
    out = []
    for w, r in zip(windows, labels):
        out.append({
            "window": w.index,
            "start": w.start,
            "end": w.end,
            "label": r["label"],
            "original_label": r["original_label"],
            "confidence": round(float(r["confidence"]), 2),
            "phase": tax.labels[r["label"]].phase if r["label"] in tax.labels else "aux",
            "is_step": tax.labels[r["label"]].is_step if r["label"] in tax.labels else False,
            "evidence": r["evidence"],
            "description": r["description"],
            "smoothed": r["label"] != r["original_label"],
            "notes": r["notes"],
        })
    return out


def merge_adjacent(refined: List[dict]) -> List[dict]:
    """Collapse consecutive windows with the same label into action segments."""
    segs = []
    for r in refined:
        if segs and segs[-1]["label"] == r["label"]:
            segs[-1]["end"] = r["end"]
            segs[-1]["windows"].append(r["window"])
            segs[-1]["confidence"] = round(
                (segs[-1]["confidence"] * (len(segs[-1]["windows"]) - 1) + r["confidence"])
                / len(segs[-1]["windows"]), 2)
        else:
            segs.append({"label": r["label"], "phase": r["phase"], "is_step": r["is_step"],
                         "start": r["start"], "end": r["end"], "confidence": r["confidence"],
                         "windows": [r["window"]]})
    return segs
