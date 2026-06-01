"""Full-resolution frame extraction (used when a real video stream is available).

Extracts up to N representative frames per window using OpenCV, mirroring the
storyboard path so the rest of the pipeline is source-agnostic.
"""
from __future__ import annotations

import os
from typing import List

from .segment import Window


def extract_window_frames(video_path: str, windows: List[Window], out_dir: str,
                          per_window: int = 3, width: int = 320) -> List[Window]:
    import cv2

    os.makedirs(out_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    for win in windows:
        # sample times at 1/4, 1/2, 3/4 of the window
        fracs = [0.5] if per_window == 1 else [(k + 1) / (per_window + 1) for k in range(per_window)]
        paths = []
        for j, fr in enumerate(fracs):
            t = win.start + fr * (win.end - win.start)
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000.0)
            ok, frame = cap.read()
            if not ok:
                continue
            h, w = frame.shape[:2]
            if w > width:
                frame = cv2.resize(frame, (width, int(h * width / w)))
            p = os.path.join(out_dir, f"w{win.index:03d}_{j}.jpg")
            cv2.imwrite(p, frame, [cv2.IMWRITE_JPEG_QUALITY, 88])
            paths.append(p)
        win.frames = paths
    cap.release()
    return windows
