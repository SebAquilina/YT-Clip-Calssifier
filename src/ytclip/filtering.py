"""Filtering + anti-hallucination validation, driven by objective features.

filter_window(...)   -> (keep: bool, reason: str)  using config/filter.yaml
validate_window(...) -> list[str] of contradiction flags between the model's
                        label/description and the computed features.

Filtered reasons: 'talking_head', 'text_overlay', 'blank'. Captioned ACTION is
kept because it has motion (text slides are static).
"""
from __future__ import annotations

import functools
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

CONFIG = Path(__file__).resolve().parents[2] / "config" / "filter.yaml"


@functools.lru_cache(maxsize=None)
def load_filter_cfg(path: str | None = None) -> dict:
    return yaml.safe_load(Path(path or CONFIG).read_text())


def filter_window(feat: Dict, cfg: dict | None = None) -> Tuple[bool, str]:
    cfg = cfg or load_filter_cfg()
    f = cfg["filter"]

    b = f["blank"]
    if feat.get("brightness", 1) < b["brightness_below"]:
        return False, "blank"
    if (feat.get("colorfulness", 1) < b["flat_colorfulness_below"]
            and feat.get("ocr_charcount", 0) < b["flat_ocr_charcount_below"]
            and feat.get("motion", 1) < b["flat_motion_below"]):
        return False, "blank"

    if feat.get("face_score", 0) >= f["talking_head"]["face_score_at_or_above"]:
        return False, "talking_head"

    t = f["text_overlay"]
    if (feat.get("ocr_charcount", 0) >= t["ocr_charcount_at_or_above"]
            and feat.get("motion", 1) < t["motion_below"]
            and feat.get("face_score", 0) < t["face_score_below"]):
        return False, "text_overlay"

    return True, ""


def has_caption(feat: Dict, cfg: dict | None = None) -> bool:
    cfg = cfg or load_filter_cfg()
    return feat.get("ocr_charcount", 0) >= cfg["caption_min_chars"]


def validate_window(label: str, description: str, feat: Dict, cfg: dict | None = None) -> List[str]:
    cfg = cfg or load_filter_cfg()
    v = cfg["validate"]
    flags: List[str] = []
    desc = (description or "").lower()

    if label == "talking_head" and feat.get("face_score", 0) < 0.2:
        flags.append("labelled talking_head but no face detected")

    if (label in v["action_step_labels"]
            and feat.get("face_score", 0) >= v["action_with_strong_face_at_or_above"]):
        flags.append(f"action label '{label}' but a strong face fills the frame")

    if (label in v["active_labels"]
            and feat.get("brightness", 1) < v["active_on_black_brightness_below"]):
        flags.append(f"active label '{label}' on a near-black frame")

    # anti-hallucination: description claims on-screen text but OCR found ~none
    claims_text = any(k in desc for k in v["caption_claim_keywords"])
    if claims_text and feat.get("ocr_charcount", 0) < cfg["caption_min_chars"]:
        flags.append("description references on-screen text but OCR found none")

    return flags


def auto_label(feat: Dict, cfg: dict | None = None) -> str | None:
    """A label suggested purely from objective features (for filtered windows so
    their label comes from the detector, not the model). None if no strong cue."""
    keep, reason = filter_window(feat, cfg)
    if not keep:
        return {"talking_head": "talking_head",
                "text_overlay": "transition",
                "blank": "transition"}[reason]
    return None
