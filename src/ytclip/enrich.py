"""Compose a richer, >50-char description for each window from grounded signals.

The vision model writes one short observation per window; ~63% are under 50
chars (terse auto-strings like "Host talks to camera."). This module *enriches*
that observation into a fuller `description_detailed` WITHOUT inventing visual
detail: every added clause is derived deterministically from data we already
have for the window --

  * the model's own observation            (the core, most-specific sentence)
  * the label's canonical meaning          (config/taxonomy.yaml description)
  * OCR'd on-screen text                    (only if it reads as real words)
  * code-computed signals                   (motion, brightness, colorfulness,
                                             dominant_colors -> qualitative prose)
  * the window's position + timing          (phase, % through video, mm:ss)

So the detail is *more context*, not hallucinated frames. Storyboard mode only
samples ~1 frame / 1.8s, so genuine per-second visual detail is not available;
this stays honest to what the signals actually support.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sqlite3

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_DIR = os.path.join(ROOT, "outputs", "db")
TAXONOMY = os.path.join(ROOT, "config", "taxonomy.yaml")

# Basic colour anchors for naming dominant_colors hex values (nearest in RGB).
_BASIC_COLORS = {
    "black": (15, 15, 15), "white": (245, 245, 245), "grey": (128, 128, 128),
    "cream": (235, 225, 200), "beige": (210, 190, 160), "brown": (120, 70, 40),
    "amber": (200, 150, 80), "orange": (230, 140, 40), "red": (200, 40, 40),
    "yellow": (230, 210, 60), "green": (70, 160, 80), "teal": (40, 150, 150),
    "blue": (55, 95, 200), "purple": (130, 70, 180), "pink": (230, 140, 175),
}


def _load_glosses(path: str = TAXONOMY) -> dict:
    with open(path) as f:
        data = yaml.safe_load(f)
    return {lid: (d.get("description", "").strip(), d.get("phase", ""))
            for lid, d in data.get("labels", {}).items()}


def _hex_to_rgb(h: str):
    h = h.strip().lstrip("#")
    if len(h) != 6:
        return None
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def _name_color(h: str):
    rgb = _hex_to_rgb(h)
    if rgb is None:
        return None
    return min(_BASIC_COLORS, key=lambda n: sum(
        (a - b) ** 2 for a, b in zip(rgb, _BASIC_COLORS[n])))


def _palette_phrase(dominant: str, colorfulness) -> str:
    hexes = [c for c in (dominant or "").split(",") if c.strip()][:2]
    if not hexes:
        return ""
    names = []
    for h in hexes:
        nm = _name_color(h)
        if nm and nm not in names:
            names.append(nm)
    try:
        c = float(colorfulness)
    except (TypeError, ValueError):
        c = None
    qual = ""
    if c is not None:
        qual = "muted " if c < 0.15 else ("vivid " if c >= 0.35 else "")
    name_part = "/".join(names) + " " if names else ""
    return f"{qual}{name_part}palette ({', '.join(hexes)})".strip()


def _motion_phrase(motion) -> str:
    try:
        m = float(motion)
    except (TypeError, ValueError):
        return ""
    if m < 0.05:
        return "static shot"
    if m < 0.15:
        return "steady, low-motion shot"
    if m < 0.35:
        return "moderate on-screen movement"
    return "lots of on-screen movement"


def _brightness_phrase(brightness) -> str:
    try:
        b = float(brightness)
    except (TypeError, ValueError):
        return ""
    if b < 0.2:
        return "dark"
    if b < 0.4:
        return "dim"
    if b < 0.7:
        return "well-lit"
    return "bright"


def _mmss(seconds) -> str:
    try:
        s = int(float(seconds))
    except (TypeError, ValueError):
        return ""
    return f"{s // 60}:{s % 60:02d}"


def _is_generic(desc: str) -> bool:
    d = (desc or "").strip().lower().rstrip(".")
    if len(d) < 24:
        return True
    return bool(re.match(r"^(host|presenter|speaker)\b.*\b(talk|talks|talking|"
                         r"present|presenting|to camera)", d)) or \
        d.startswith("blank") or d.startswith("empty")


def enrich_description(row: dict, glosses: dict | None = None) -> str:
    """Return a fuller (>=50 char where possible) description for one window."""
    glosses = glosses if glosses is not None else _load_glosses()
    core = (row.get("description") or "").strip()
    label = row.get("action_label", "")
    gloss, phase = glosses.get(label, ("", row.get("phase", "")))
    phase = row.get("phase") or phase

    clauses: list[str] = []
    if core:
        clauses.append(core.rstrip(". "))
    # canonical meaning of the step -- add when the core line is thin/generic
    if gloss and (not core or _is_generic(core)):
        clauses.append(gloss.rstrip(". "))

    # NB: raw `ocr_text` is the project's noisy validation signal, not display
    # text -- the model's `description` already quotes legible captions. We only
    # surface the reliable has_caption bit, never the raw (often garbled) OCR.
    visual = ", ".join(p for p in (
        "captioned" if row.get("has_caption") else "",
        _motion_phrase(row.get("motion")),
        _brightness_phrase(row.get("brightness")),
        _palette_phrase(row.get("dominant_colors"), row.get("colorfulness")),
    ) if p)
    if visual:
        clauses.append(visual)

    # position / timing context
    bits = []
    if phase:
        bits.append(f"{phase} phase")
    dur = row.get("video_duration_s")
    start = row.get("start_s")
    try:
        if dur and float(dur) > 0 and start is not None:
            bits.append(f"~{round(100 * float(start) / float(dur))}% in")
    except (TypeError, ValueError):
        pass
    span = "–".join(x for x in (_mmss(row.get("start_s")), _mmss(row.get("end_s"))) if x)
    if span:
        bits.append(span)
    if bits:
        clauses.append(", ".join(bits))

    out = ". ".join(c for c in clauses if c).strip()
    if out and not out.endswith("."):
        out += "."
    return out


# ---------------------------------------------------------------------------
# Backfill `description_detailed` into the already-built database files.
# ---------------------------------------------------------------------------
_TARGETS = ["classifications", "classifications_clean"]


def _read_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def enrich_db() -> dict:
    """Add a `description_detailed` column to the built db files (jsonl/csv/sqlite).

    Reads the already-built outputs/db/classifications*.jsonl, so it needs no
    data/work intermediates. Re-run `ytclip split-db` afterwards to propagate
    the new column into the per-label shards.
    """
    glosses = _load_glosses()
    base = _read_jsonl(os.path.join(DB_DIR, "classifications.jsonl"))
    if not base:
        raise FileNotFoundError(
            "outputs/db/classifications.jsonl not found - run `ytclip build-db` first")

    # field order: insert description_detailed right after description
    fields = list(base[0].keys())
    if "description_detailed" not in fields:
        fields.insert(fields.index("description") + 1, "description_detailed")

    lengths = []
    for name in _TARGETS:
        jp = os.path.join(DB_DIR, f"{name}.jsonl")
        if not os.path.exists(jp):
            continue
        rows = _read_jsonl(jp)
        out_rows = []
        for r in rows:
            detail = enrich_description(r, glosses)
            if name == "classifications":
                lengths.append(len(detail))
            out_rows.append({**{f: r.get(f, "") for f in fields},
                             "description_detailed": detail})
        with open(jp, "w") as f:
            for r in out_rows:
                f.write(json.dumps(r) + "\n")
        with open(os.path.join(DB_DIR, f"{name}.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(out_rows)

    _enrich_sqlite(glosses)

    n = len(lengths) or 1
    return {
        "rows": len(lengths),
        "mean_len": round(sum(lengths) / n, 1),
        "min_len": min(lengths) if lengths else 0,
        "over_50": sum(1 for x in lengths if x > 50),
        "dir": DB_DIR,
    }


def _enrich_sqlite(glosses: dict):
    dbp = os.path.join(DB_DIR, "classifications.sqlite")
    if not os.path.exists(dbp):
        return
    con = sqlite3.connect(dbp)
    cur = con.cursor()
    cols = [c[1] for c in cur.execute("PRAGMA table_info(windows)").fetchall()]
    if "description_detailed" not in cols:
        cur.execute("ALTER TABLE windows ADD COLUMN description_detailed TEXT")
    colnames = [c[1] for c in cur.execute("PRAGMA table_info(windows)").fetchall()]
    rows = cur.execute("SELECT rowid, * FROM windows").fetchall()
    for row in rows:
        rec = dict(zip(["rowid"] + colnames, row))
        detail = enrich_description(rec, glosses)
        cur.execute("UPDATE windows SET description_detailed=? WHERE rowid=?",
                    (detail, rec["rowid"]))
    con.commit()
    con.close()
