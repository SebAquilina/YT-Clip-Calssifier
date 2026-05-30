"""Tests for the objective filter + anti-hallucination validator."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ytclip.filtering import filter_window, validate_window, has_caption, auto_label


def _f(**kw):
    base = dict(face_score=0.0, text_score=0.0, ocr_text="", ocr_charcount=0,
                motion=0.2, brightness=0.6, colorfulness=0.2)
    base.update(kw)
    return base


def test_talking_head_filtered_by_face():
    keep, reason = filter_window(_f(face_score=0.8))
    assert keep is False and reason == "talking_head"


def test_static_text_card_filtered():
    keep, reason = filter_window(_f(ocr_charcount=40, motion=0.0))
    assert keep is False and reason == "text_overlay"


def test_captioned_action_is_kept():
    # has OCR text but it MOVES -> hands-on action with a caption, keep it
    keep, reason = filter_window(_f(ocr_charcount=40, motion=0.15))
    assert keep is True and reason == ""


def test_blank_frame_filtered():
    keep, reason = filter_window(_f(brightness=0.03))
    assert keep is False and reason == "blank"


def test_plain_action_kept():
    keep, reason = filter_window(_f(motion=0.2, brightness=0.8))
    assert keep is True


def test_validator_flags_action_with_face():
    flags = validate_window("pour_wax", "pouring wax", _f(face_score=0.7))
    assert any("strong face" in f for f in flags)


def test_validator_flags_unsupported_caption_claim():
    flags = validate_window("transition", "title card with 'subscribe' caption", _f(ocr_charcount=0))
    assert any("OCR found none" in f for f in flags)


def test_auto_label_maps_reasons():
    assert auto_label(_f(face_score=0.9)) == "talking_head"
    assert auto_label(_f(ocr_charcount=40, motion=0.0)) == "transition"
    assert auto_label(_f(motion=0.2)) is None  # kept action -> no auto label


def test_has_caption_threshold():
    assert has_caption(_f(ocr_charcount=12)) is True
    assert has_caption(_f(ocr_charcount=2)) is False
