"""Orchestration: prepare -> (classify) -> finalize -> learn.

Because no standalone Anthropic API key is available in this environment, the
vision-classification step is performed by an agent that reads the contact
sheets produced by `prepare` and writes a labels file. `prepare` and `finalize`
are therefore separate phases joined by ``<vid>.labels.json``.

Layout:
  data/work/<vid>/frames|thumbs/   working images   (gitignored)
  data/work/<vid>/sheets/          contact sheets    (gitignored)
  data/work/<vid>/windows.json     window manifest + meta
  outputs/<vid>.labels.json        raw labels (from the classifier)
  outputs/<vid>.timeline.json      refined timeline
  outputs/<vid>.md                 human report
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict
from typing import List, Optional

from . import download, frames as frames_mod, montage, report, storyboard
from .rules import refine
from .segment import (Window, detect_shots, windows_from_shots, windows_from_thumbs)
from .taxonomy import load_rules, load_taxonomy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORK = os.path.join(ROOT, "data", "work")
OUT = os.path.join(ROOT, "outputs")


def _work(vid: str) -> str:
    d = os.path.join(WORK, vid)
    os.makedirs(d, exist_ok=True)
    return d


def prepare(video_id: str, prefer_stream: bool = True, max_height: int = 480) -> dict:
    """Acquire frames, build windows + contact sheets. Returns the manifest."""
    work = _work(video_id)
    info = download.probe(video_id)
    if not info:
        raise RuntimeError(f"could not probe {video_id} (bot-gated or unavailable)")
    meta = {"id": video_id, "title": info.get("title", ""),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "duration": float(info.get("duration") or 0),
            "uploader": info.get("uploader", "")}

    windows: List[Window] = []
    source = "storyboard"

    if prefer_stream:
        path = download.try_download_video(video_id, os.path.join(work, "video"), max_height)
        if path:
            shots = detect_shots(path)
            windows = windows_from_shots(shots, meta["duration"])
            windows = frames_mod.extract_window_frames(
                path, windows, os.path.join(work, "frames"))
            source = "stream"

    if not windows:  # storyboard fallback
        thumbs = storyboard.fetch_thumbs(video_id, os.path.join(work, "thumbs"), info=info)
        if not thumbs:
            raise RuntimeError(f"no stream and no storyboard for {video_id}")
        windows = windows_from_thumbs(thumbs, meta["duration"])

    meta["source"] = source
    sheets = montage.build_sheets(windows, os.path.join(work, "sheets"), video_id)

    manifest = {
        "meta": meta,
        "source": source,
        "windows": [{"index": w.index, "start": w.start, "end": w.end,
                     "frames": w.frames} for w in windows],
        "sheets": sheets,
    }
    with open(os.path.join(work, "windows.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    return manifest


def load_manifest(video_id: str) -> dict:
    with open(os.path.join(_work(video_id), "windows.json")) as f:
        return json.load(f)


def finalize(video_id: str) -> dict:
    """Read <vid>.labels.json + window manifest, run the rules engine, write
    timeline + markdown."""
    manifest = load_manifest(video_id)
    windows = [Window(**w) for w in manifest["windows"]]
    with open(os.path.join(OUT, f"{video_id}.labels.json")) as f:
        raw = json.load(f)
    raw_by_idx = {r["window"]: r for r in raw}
    aligned = [raw_by_idx.get(w.index, {"label": "other_unclear", "confidence": 0.0,
                                        "evidence": "no label"}) for w in windows]

    tax = load_taxonomy()
    refined = refine(windows, aligned, tax)
    meta = dict(manifest["meta"]); meta["source"] = manifest["source"]
    doc = report.write_timeline(meta, refined, os.path.join(OUT, f"{video_id}.timeline.json"))
    report.write_markdown(doc, os.path.join(OUT, f"{video_id}.md"))
    return doc


def make_label_stub(video_id: str) -> str:
    """Write an empty labels stub for the classifier to fill in."""
    manifest = load_manifest(video_id)
    stub = [{"window": w["index"], "start": w["start"], "end": w["end"],
             "label": "", "confidence": 0.0, "description": ""} for w in manifest["windows"]]
    p = os.path.join(OUT, f"{video_id}.labels.json")
    os.makedirs(OUT, exist_ok=True)
    with open(p, "w") as f:
        json.dump(stub, f, indent=2)
    return p


def autolabel_stub(video_id: str) -> dict:
    """Compute features, then pre-label the windows the objective detectors flag
    as talking-head / text-card / blank, leaving the ACTION-candidate windows
    blank for the agent to describe. This both speeds up new videos and grounds
    the easy-but-error-prone aux windows in detectors rather than guesses.

    Returns {"todo": [window indices needing manual labels], "auto": n}.
    """
    from .features import compute_for_video
    from .filtering import filter_window, has_caption
    manifest = load_manifest(video_id)
    feats = compute_for_video(video_id, WORK)
    rows, todo, auto = [], [], 0
    n = len(manifest["windows"])
    for wd in manifest["windows"]:
        i = wd["index"]
        ft = feats.get(i, {})
        keep, reason = filter_window(ft)
        rec = {"window": i, "start": wd["start"], "end": wd["end"],
               "label": "", "confidence": 0.0, "description": ""}
        if not keep:
            ocr = ft.get("ocr_text", "")
            if reason == "talking_head":
                rec.update(label="talking_head", confidence=round(0.5 + 0.4 * ft.get("face_score", 0), 2),
                           description="Presenter talking to camera (auto-detected: frontal face).")
            elif reason == "text_overlay":
                pos = i / max(1, n - 1)
                lbl = "intro_titlecard" if pos < 0.15 else "outro_cta" if pos > 0.85 else "transition"
                cap = f" Text reads: '{ocr}'." if has_caption(ft) else ""
                rec.update(label=lbl, confidence=0.5,
                           description=f"On-screen text card (auto-detected: static frame, OCR text).{cap}")
            else:  # blank
                rec.update(label="transition", confidence=0.5,
                           description="Blank / near-black frame (auto-detected).")
            auto += 1
        else:
            todo.append(i)
        rows.append(rec)
    p = os.path.join(OUT, f"{video_id}.labels.json")
    os.makedirs(OUT, exist_ok=True)
    with open(p, "w") as f:
        json.dump(rows, f, indent=2)
    return {"path": p, "todo": todo, "auto": auto, "n": n}
