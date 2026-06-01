"""Build 5-10s windows and attach representative frames to each.

Two entry points:
  windows_from_thumbs(...)  - storyboard mode (uniform time windows)
  windows_from_shots(...)   - full-res mode (snap to PySceneDetect shot cuts)

A Window never exceeds rules.windowing.max_seconds (hard cap 10s).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .storyboard import Thumb
from .taxonomy import load_rules


@dataclass
class Window:
    index: int
    start: float
    end: float
    frames: List[str] = field(default_factory=list)   # representative image paths

    @property
    def duration(self) -> float:
        return round(self.end - self.start, 2)

    @property
    def mid(self) -> float:
        return round((self.start + self.end) / 2, 2)


def _grid(total: float, lo: float, hi: float, target: float) -> List[tuple]:
    """Tile [0, total] into spans, each within [lo, hi], close to target."""
    spans, t = [], 0.0
    if total <= 0:
        return spans
    n = max(1, round(total / target))
    step = total / n
    # keep step within bounds where possible
    step = max(lo, min(hi, step))
    while t < total - 1e-6:
        end = min(total, t + step)
        if total - end < lo and total - end > 0:   # avoid a tiny trailing window
            end = total
        spans.append((round(t, 2), round(end, 2)))
        t = end
    return spans


def windows_from_thumbs(thumbs: List[Thumb], duration: float,
                        max_frames_per_window: int = 3, rules: dict | None = None) -> List[Window]:
    rules = rules or load_rules()
    w = rules["windowing"]
    spans = _grid(duration, w["min_seconds"], w["max_seconds"], w["target_seconds"])
    windows: List[Window] = []
    for i, (s, e) in enumerate(spans):
        inside = [t for t in thumbs if s <= t.t < e] or \
                 [min(thumbs, key=lambda t: abs(t.t - (s + e) / 2))] if thumbs else []
        # pick up to N spread across the window (first, middle, last)
        chosen = inside
        if len(inside) > max_frames_per_window:
            idxs = [0, len(inside) // 2, len(inside) - 1][:max_frames_per_window]
            chosen = [inside[j] for j in sorted(set(idxs))]
        windows.append(Window(index=i, start=s, end=e, frames=[t.path for t in chosen]))
    return windows


def detect_shots(video_path: str, threshold: float = 27.0) -> List[tuple]:
    """Return list of (start_s, end_s) shot spans using PySceneDetect."""
    from scenedetect import detect, ContentDetector
    scenes = detect(video_path, ContentDetector(threshold=threshold))
    return [(s.get_seconds(), e.get_seconds()) for s, e in scenes]


def windows_from_shots(shots: List[tuple], duration: float, rules: dict | None = None) -> List[Window]:
    """Snap windows to shot cuts, then enforce the 5-10s bounds: split long shots,
    merge short ones."""
    rules = rules or load_rules()
    w = rules["windowing"]
    lo, hi, target = w["min_seconds"], w["max_seconds"], w["target_seconds"]
    if not shots:
        shots = [(0.0, duration)]

    # 1) split any shot longer than hi into ~target sub-spans
    spans: List[tuple] = []
    for s, e in shots:
        for sub in _grid(e - s, lo, hi, target):
            spans.append((round(s + sub[0], 2), round(s + sub[1], 2)))

    # 2) merge spans shorter than lo into the next one (without exceeding hi)
    merged: List[tuple] = []
    for s, e in spans:
        if merged and (merged[-1][1] - merged[-1][0]) < lo and (e - merged[-1][0]) <= hi:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))

    return [Window(index=i, start=s, end=e) for i, (s, e) in enumerate(merged)]
