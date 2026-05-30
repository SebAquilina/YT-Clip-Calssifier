"""Write per-video outputs: JSON timeline + human-readable markdown."""
from __future__ import annotations

import json
import os
from typing import List

from .rules import merge_adjacent


def _fmt(t: float) -> str:
    m, s = divmod(int(round(t)), 60)
    return f"{m:01d}:{s:02d}"


def write_timeline(meta: dict, refined: List[dict], out_path: str) -> dict:
    segments = merge_adjacent(refined)
    doc = {
        "video_id": meta["id"],
        "title": meta["title"],
        "url": meta["url"],
        "duration": meta["duration"],
        "source": meta.get("source", "storyboard"),
        "n_windows": len(refined),
        "windows": refined,
        "segments": segments,
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(doc, f, indent=2)
    return doc


def write_markdown(doc: dict, out_path: str) -> None:
    lines = [
        f"# {doc['title']}",
        "",
        f"- **Video:** [{doc['video_id']}]({doc['url']})",
        f"- **Duration:** {_fmt(doc['duration'])}  ({doc['duration']:.0f}s)",
        f"- **Source:** {doc['source']}  |  **Windows:** {doc['n_windows']}  |  "
        f"**Segments:** {len(doc['segments'])}",
        "",
        "## Action segments (merged)",
        "",
        "| # | Time | Duration | Action | Phase | Step | Conf |",
        "|--:|------|---------:|--------|-------|:----:|-----:|",
    ]
    for i, s in enumerate(doc["segments"], 1):
        dur = s["end"] - s["start"]
        lines.append(
            f"| {i} | {_fmt(s['start'])}–{_fmt(s['end'])} | {dur:.0f}s | "
            f"`{s['label']}` | {s['phase']} | {'✓' if s['is_step'] else ''} | {s['confidence']:.2f} |")

    lines += ["", "## Per-window detail", "",
              "| Window | Time | Action | Conf | Notes |",
              "|-------:|------|--------|-----:|-------|"]
    for w in doc["windows"]:
        notes = "; ".join(w.get("notes", []))
        smell = " *(smoothed)*" if w.get("smoothed") else ""
        lines.append(
            f"| W{w['window']} | {_fmt(w['start'])}–{_fmt(w['end'])} | "
            f"`{w['label']}`{smell} | {w['confidence']:.2f} | {notes} |")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
