"""Fetch YouTube storyboards and slice them into timestamped thumbnails.

A storyboard "format" (id ``sbN``) is a set of sheet images, each a grid of
``rows x columns`` thumbnails sampled at a fixed interval across the video. This
gives us a frame roughly every 1-3s with no video download - the only visual
signal reachable from a bot-gated IP.
"""
from __future__ import annotations

import io
import os
from dataclasses import dataclass
from typing import List, Optional

import requests
from PIL import Image

from .download import probe


@dataclass
class Thumb:
    index: int
    t: float          # timestamp (seconds) at the centre of the thumbnail
    path: str


def _pick_storyboard(info: dict) -> Optional[dict]:
    sbs = [f for f in info.get("formats", []) if str(f.get("format_id", "")).startswith("sb")]
    if not sbs:
        return None
    # Highest resolution sheet (largest tile width).
    return max(sbs, key=lambda f: (f.get("width") or 0))


def fetch_thumbs(video_id: str, out_dir: str, info: dict | None = None) -> List[Thumb]:
    """Download storyboard sheets for a video and slice them into per-thumbnail
    JPEGs. Returns thumbnails ordered by time. Empty list if no storyboard."""
    info = info or probe(video_id)
    if not info:
        return []
    sb = _pick_storyboard(info)
    if not sb:
        return []

    duration = float(info.get("duration") or 0)
    rows, cols = int(sb.get("rows") or 0), int(sb.get("columns") or 0)
    tile_w, tile_h = int(sb.get("width") or 0), int(sb.get("height") or 0)
    frags = sb.get("fragments") or []
    if not (rows and cols and tile_w and tile_h and frags):
        return []

    os.makedirs(out_dir, exist_ok=True)
    per_sheet = rows * cols
    total = per_sheet * len(frags)
    interval = duration / total if total else 2.0

    thumbs: List[Thumb] = []
    idx = 0
    for frag in frags:
        try:
            resp = requests.get(frag["url"], timeout=30)
            resp.raise_for_status()
            sheet = Image.open(io.BytesIO(resp.content)).convert("RGB")
        except Exception:
            idx += per_sheet
            continue
        for r in range(rows):
            for c in range(cols):
                box = (c * tile_w, r * tile_h, (c + 1) * tile_w, (r + 1) * tile_h)
                tile = sheet.crop(box)
                # Skip blank padding tiles at the end (storyboards over-allocate).
                if tile.getbbox() is None:
                    idx += 1
                    continue
                t = (idx + 0.5) * interval
                if duration and t > duration + interval:
                    idx += 1
                    continue
                path = os.path.join(out_dir, f"t{idx:04d}.jpg")
                tile.save(path, quality=90)
                thumbs.append(Thumb(index=idx, t=round(t, 2), path=path))
                idx += 1
    return thumbs
