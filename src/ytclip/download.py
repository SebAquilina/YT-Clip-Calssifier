"""YouTube access via yt-dlp.

Two responsibilities:
  1. metadata / search
  2. obtaining *frames* for a video, by either
       a) downloading the real video stream (best quality), or
       b) falling back to YouTube storyboards (low-res thumbnail sheets) when the
          stream is unavailable - e.g. bot-gated cloud IPs.

TLS note: this environment routes egress through an inspecting proxy whose CA is
already in the system trust store (/etc/ssl/certs/ca-certificates.crt) but NOT in
certifi. yt-dlp uses certifi by default, so we pass `--compat-options no-certifi`
(option key ``compat_opts: ['no-certifi']``) which makes yt-dlp use the system
trust store. This trusts an already-trusted CA; it does NOT disable verification.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

import yt_dlp

# Player clients to try, in order. `mweb` reliably exposes storyboards even when
# muxed streams are bot-gated; default/web are tried first for real streams.
STREAM_CLIENTS = ["default", "web_embedded", "mweb"]
STORYBOARD_CLIENTS = ["mweb", "web_embedded", "default"]


def _base_opts(**extra) -> dict:
    opts = {
        "compat_opts": ["no-certifi"],   # use system trust store (egress CA lives there)
        "quiet": True,
        "no_warnings": True,
    }
    opts.update(extra)
    return opts


@dataclass
class VideoMeta:
    id: str
    title: str
    duration: float
    url: str
    uploader: str = ""


def search(query: str, n: int = 10, dmin: int = 90, dmax: int = 600) -> List[VideoMeta]:
    """Flat search; returns metadata only (cheap, not bot-gated)."""
    out: List[VideoMeta] = []
    with yt_dlp.YoutubeDL(_base_opts(extract_flat=True)) as ydl:
        info = ydl.extract_info(f"ytsearch{n*3}:{query}", download=False)
        for e in info.get("entries", []):
            d = e.get("duration") or 0
            if dmin <= d <= dmax:
                out.append(VideoMeta(
                    id=e["id"], title=(e.get("title") or "")[:120],
                    duration=float(d), url=f"https://www.youtube.com/watch?v={e['id']}",
                    uploader=e.get("uploader") or e.get("channel") or "",
                ))
            if len(out) >= n:
                break
    return out


def probe(video_id: str) -> Optional[dict]:
    """Return full info dict for a single video (tries storyboard client so it
    survives bot-gating). None on failure."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    for client in STORYBOARD_CLIENTS:
        opts = _base_opts(skip_download=True, ignore_no_formats_error=True,
                          extractor_args={"youtube": {"player_client": [client]}})
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception:
            continue
    return None


def try_download_video(video_id: str, dest_dir: str, max_height: int = 480) -> Optional[str]:
    """Attempt to download a real (muxed) stream. Returns path or None if every
    client is bot-gated / DRM-only."""
    os.makedirs(dest_dir, exist_ok=True)
    url = f"https://www.youtube.com/watch?v={video_id}"
    fmt = (f"bv*[height<={max_height}][ext=mp4]+ba[ext=m4a]/"
           f"b[height<={max_height}]/b[height<={max_height}]/b")
    for client in STREAM_CLIENTS:
        opts = _base_opts(
            format=fmt, merge_output_format="mp4",
            outtmpl=os.path.join(dest_dir, "%(id)s.%(ext)s"),
            extractor_args={"youtube": {"player_client": [client]}},
        )
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            path = os.path.join(dest_dir, f"{video_id}.mp4")
            if os.path.exists(path) and os.path.getsize(path) > 0:
                return path
        except Exception:
            continue
    return None
