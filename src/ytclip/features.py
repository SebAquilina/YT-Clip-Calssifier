"""Objective per-window visual features — computed by code, not by the model.

These are the anti-hallucination backbone: each window gets reproducible
measurements that can corroborate or contradict the model's label/description:

  face_score      fraction of the window's frames with a sizeable frontal face
                  (-> talking-head signal)              [OpenCV Haar cascade]
  text_score      estimated fraction of frame area covered by text-like regions
                  (-> text-overlay signal)              [OpenCV MSER]
  ocr_text        verbatim text read off the frame (so caption claims come from
                  Tesseract, not the model)             [pytesseract]
  ocr_charcount   length of cleaned OCR text
  brightness      mean luma 0..1 (near-0 => black/blank frame)
  colorfulness    Hasler-Suesstrunk metric (low => greyscale/text slide)
  motion          mean abs frame-diff across the window (0 => static)
  dominant_colors top hex colours

Results are cached at data/work/<vid>/features.json.

NOTE ON RESOLUTION: source frames are 160x90 YouTube storyboard tiles, so these
detectors are heuristic. Frames are upscaled before detection and every raw
score is stored, so decisions made from them stay auditable rather than trusted
blindly.
"""
from __future__ import annotations

import json
import os
import re
from typing import Dict, List

import cv2
import numpy as np

_FACE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
_MSER = cv2.MSER_create()
_MSER.setMinArea(8)
_MSER.setMaxArea(2000)

try:
    import pytesseract
    _HAS_OCR = True
except Exception:
    _HAS_OCR = False


def _load(path: str):
    if not os.path.exists(path):
        return None
    img = cv2.imread(path)
    return img


def _upscale(img, factor=4):
    h, w = img.shape[:2]
    return cv2.resize(img, (w * factor, h * factor), interpolation=cv2.INTER_CUBIC)


def _brightness(img) -> float:
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(g.mean()) / 255.0


def _colorfulness(img) -> float:
    # Hasler & Suesstrunk (2003)
    b, g, r = cv2.split(img.astype("float"))
    rg = np.absolute(r - g)
    yb = np.absolute(0.5 * (r + g) - b)
    std = np.sqrt(rg.std() ** 2 + yb.std() ** 2)
    mean = np.sqrt(rg.mean() ** 2 + yb.mean() ** 2)
    return float(std + 0.3 * mean) / 255.0


def _face_area_frac(img) -> float:
    big = _upscale(img, 4)
    gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    H, W = gray.shape
    faces = _FACE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4,
                                   minSize=(int(W * 0.12), int(H * 0.12)))
    if len(faces) == 0:
        return 0.0
    return float(max(w * h for (x, y, w, h) in faces)) / float(W * H)


def _text_coverage(img) -> float:
    big = _upscale(img, 4)
    gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)
    H, W = gray.shape
    try:
        regions, _ = _MSER.detectRegions(gray)
    except Exception:
        return 0.0
    mask = np.zeros((H, W), np.uint8)
    for p in regions:
        x, y, w, h = cv2.boundingRect(p.reshape(-1, 1, 2))
        ar = w / float(h + 1e-6)
        # text glyphs: not too tall/wide, modest size
        if 0.1 < ar < 8 and 4 < h < H * 0.5:
            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
    return float((mask > 0).sum()) / float(W * H)


_OCR_CLEAN = re.compile(r"[^A-Za-z0-9 %&°.,/+\-:!?'$]")


def _ocr(img) -> str:
    if not _HAS_OCR:
        return ""
    big = _upscale(img, 5)
    gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 5, 50, 50)
    try:
        txt = pytesseract.image_to_string(gray, config="--psm 6")
    except Exception:
        return ""
    txt = _OCR_CLEAN.sub(" ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    # keep only tokens with >=2 alpha chars to drop OCR noise
    toks = [t for t in txt.split() if sum(c.isalpha() for c in t) >= 2 or t.replace('.', '').isdigit()]
    return " ".join(toks)[:200]


def _dominant_colors(img, k=3) -> List[str]:
    small = cv2.resize(img, (32, 18)).reshape(-1, 3).astype("float32")
    try:
        _, labels, centers = cv2.kmeans(
            small, k, None,
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0), 3, cv2.KMEANS_PP_CENTERS)
        counts = np.bincount(labels.flatten())
        order = np.argsort(-counts)
        return ["#%02x%02x%02x" % (int(centers[i][2]), int(centers[i][1]), int(centers[i][0])) for i in order]
    except Exception:
        return []


def window_features(frame_paths: List[str], do_ocr=True) -> Dict:
    imgs = [im for im in (_load(p) for p in frame_paths) if im is not None]
    if not imgs:
        return {"face_score": 0, "text_score": 0, "ocr_text": "", "ocr_charcount": 0,
                "brightness": 0, "colorfulness": 0, "motion": 0, "dominant_colors": [], "n_frames": 0}

    faces = [_face_area_frac(im) for im in imgs]
    texts = [_text_coverage(im) for im in imgs]
    bright = [_brightness(im) for im in imgs]
    color = [_colorfulness(im) for im in imgs]

    # motion: mean abs diff between consecutive frames (resized to common size)
    motion = 0.0
    if len(imgs) > 1:
        ref = cv2.cvtColor(cv2.resize(imgs[0], (160, 90)), cv2.COLOR_BGR2GRAY).astype("float")
        diffs = []
        for im in imgs[1:]:
            g = cv2.cvtColor(cv2.resize(im, (160, 90)), cv2.COLOR_BGR2GRAY).astype("float")
            diffs.append(np.abs(g - ref).mean() / 255.0)
            ref = g
        motion = float(np.mean(diffs))

    mid = imgs[len(imgs) // 2]
    # only OCR if there is text-like content, to keep it cheap
    ocr_text = ""
    if do_ocr and max(texts) > 0.02:
        ocr_text = _ocr(mid)

    return {
        "face_score": round(float(np.mean([1.0 if f > 0.04 else 0.0 for f in faces])), 3),
        "face_area_max": round(float(max(faces)), 3),
        "text_score": round(float(np.mean(texts)), 3),
        "ocr_text": ocr_text,
        "ocr_charcount": len(ocr_text),
        "brightness": round(float(np.mean(bright)), 3),
        "colorfulness": round(float(np.mean(color)), 3),
        "motion": round(motion, 3),
        "dominant_colors": _dominant_colors(mid),
        "n_frames": len(imgs),
    }


def compute_for_video(video_id: str, work_root: str, do_ocr=True) -> Dict[int, Dict]:
    manifest = json.load(open(os.path.join(work_root, video_id, "windows.json")))
    out = {}
    for wd in manifest["windows"]:
        out[wd["index"]] = window_features(wd.get("frames", []), do_ocr=do_ocr)
    cache = os.path.join(work_root, video_id, "features.json")
    json.dump(out, open(cache, "w"))
    return out
