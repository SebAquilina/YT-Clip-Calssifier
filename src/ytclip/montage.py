"""Build labelled contact sheets from windows for vision classification.

Each tile = one window, rendered as a horizontal strip of that window's
representative frames with a caption ``W{index}  {start}-{end}s``. Tiles are
packed into a grid; large videos spill onto multiple sheets. A vision model (or
the agent) reads a sheet and emits one label per window index.
"""
from __future__ import annotations

import math
import os
from typing import List

from PIL import Image, ImageDraw, ImageFont

from .segment import Window

TILE_H = 150          # px height of each frame strip
CAP_H = 22            # caption bar height
COLS = 4              # windows per row
PAD = 6
MAX_TILES_PER_SHEET = 24


def _font(size: int = 14):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _tile(win: Window) -> Image.Image:
    frames = [Image.open(p).convert("RGB") for p in win.frames if os.path.exists(p)]
    if not frames:
        strip = Image.new("RGB", (int(TILE_H * 16 / 9), TILE_H), (40, 40, 40))
    else:
        scaled = []
        for im in frames:
            w = int(im.width * TILE_H / im.height)
            scaled.append(im.resize((w, TILE_H)))
        total_w = sum(im.width for im in scaled) + PAD * (len(scaled) - 1)
        strip = Image.new("RGB", (total_w, TILE_H), (0, 0, 0))
        x = 0
        for im in scaled:
            strip.paste(im, (x, 0))
            x += im.width + PAD

    tile = Image.new("RGB", (strip.width, TILE_H + CAP_H), (20, 20, 20))
    tile.paste(strip, (0, CAP_H))
    d = ImageDraw.Draw(tile)
    d.text((4, 3), f"W{win.index}  {win.start:.0f}-{win.end:.0f}s", fill=(255, 230, 120), font=_font(14))
    return tile


def build_sheets(windows: List[Window], out_dir: str, video_id: str) -> List[str]:
    os.makedirs(out_dir, exist_ok=True)
    paths: List[str] = []
    chunks = [windows[i:i + MAX_TILES_PER_SHEET] for i in range(0, len(windows), MAX_TILES_PER_SHEET)]
    for si, chunk in enumerate(chunks):
        tiles = [_tile(w) for w in chunk]
        tw = max(t.width for t in tiles)
        th = max(t.height for t in tiles)
        rows = math.ceil(len(tiles) / COLS)
        sheet = Image.new("RGB", (COLS * tw + PAD * (COLS + 1),
                                  rows * th + PAD * (rows + 1)), (12, 12, 12))
        for i, t in enumerate(tiles):
            r, c = divmod(i, COLS)
            sheet.paste(t, (PAD + c * (tw + PAD), PAD + r * (th + PAD)))
        p = os.path.join(out_dir, f"{video_id}_sheet{si}.jpg")
        sheet.save(p, quality=90)
        paths.append(p)
    return paths
