"""Build the consolidated classification database from finalized timelines.

Each window row carries, alongside the model's label + description:
  * objective code-computed features (face_score, text_score, ocr_text, motion,
    brightness, colorfulness, dominant_colors)  -- the anti-hallucination signals
  * keep / filter_reason   (talking-head / text-overlay / blank filtering)
  * validation_flags       (label<->evidence contradictions to review)

Outputs in outputs/db/:
  classifications.{sqlite,csv,jsonl}        ALL windows (with keep flag)
  classifications_clean.{csv,jsonl}         action-only subset (keep & is_step)
The SQLite file also exposes a `windows_clean` view.
"""
from __future__ import annotations

import csv
import glob
import json
import os
import sqlite3

from .filtering import filter_window, has_caption, validate_window

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "outputs")
WORK = os.path.join(ROOT, "data", "work")
DB_DIR = os.path.join(OUT, "db")

WINDOW_FIELDS = [
    "video_id", "video_url", "video_title", "video_duration_s", "source",
    "window_index", "start_s", "end_s", "duration_s", "window_url",
    "action_label", "phase", "is_step", "confidence", "description",
    "description_detailed",
    # objective features (computed by code, not the model):
    "ocr_text", "has_caption", "face_score", "text_score", "motion",
    "brightness", "colorfulness", "dominant_colors",
    # filtering + validation:
    "keep", "filter_reason", "validation_flags",
]


def _features(video_id: str) -> dict:
    p = os.path.join(WORK, video_id, "features.json")
    if not os.path.exists(p):
        return {}
    return {int(k): v for k, v in json.load(open(p)).items()}


def _timelines():
    for p in sorted(glob.glob(os.path.join(OUT, "*.timeline.json"))):
        with open(p) as f:
            yield json.load(f)


def _row_for_window(d, wdw, feats, glosses):
    from .enrich import enrich_description
    vid = d["video_id"]
    i = wdw["window"]
    ft = feats.get(i, {})
    start = int(round(wdw["start"]))
    keep, reason = (filter_window(ft) if ft else (True, ""))
    flags = validate_window(wdw["label"], wdw.get("description", ""), ft) if ft else []
    row = {
        "video_id": vid,
        "video_url": d["url"],
        "video_title": d["title"],
        "video_duration_s": d["duration"],
        "source": d.get("source", "storyboard"),
        "window_index": i,
        "start_s": wdw["start"],
        "end_s": wdw["end"],
        "duration_s": round(wdw["end"] - wdw["start"], 2),
        "window_url": f"https://youtu.be/{vid}?t={start}s",
        "action_label": wdw["label"],
        "phase": wdw.get("phase", ""),
        "is_step": int(bool(wdw.get("is_step"))),
        "confidence": wdw.get("confidence", 0.0),
        "description": wdw.get("description") or wdw.get("evidence", ""),
        "description_detailed": "",
        "ocr_text": ft.get("ocr_text", ""),
        "has_caption": int(has_caption(ft)) if ft else 0,
        "face_score": ft.get("face_score", ""),
        "text_score": ft.get("text_score", ""),
        "motion": ft.get("motion", ""),
        "brightness": ft.get("brightness", ""),
        "colorfulness": ft.get("colorfulness", ""),
        "dominant_colors": ",".join(ft.get("dominant_colors", [])),
        "keep": int(keep),
        "filter_reason": reason,
        "validation_flags": "; ".join(flags),
    }
    row["description_detailed"] = enrich_description(row, glosses)
    return row


def rows_for_video(video_id: str) -> list:
    """Build the db rows for a single finalized video (used by the shared store)."""
    from .enrich import _load_glosses
    p = os.path.join(OUT, f"{video_id}.timeline.json")
    if not os.path.exists(p):
        raise FileNotFoundError(f"no timeline for {video_id}: run `ytclip finalize {video_id}` first")
    with open(p) as f:
        d = json.load(f)
    feats = _features(video_id)
    glosses = _load_glosses()
    return [_row_for_window(d, wdw, feats, glosses) for wdw in d["windows"]]


def _rows():
    from .enrich import _load_glosses
    glosses = _load_glosses()
    for d in _timelines():
        feats = _features(d["video_id"])
        for wdw in d["windows"]:
            yield _row_for_window(d, wdw, feats, glosses)


def _is_action(r: dict) -> bool:
    # the clean subset = passed the objective filter AND is a hands-on action step
    return bool(r["keep"]) and bool(r["is_step"])


def _write_csv(path, rows):
    with open(path, "w", newline="") as f:
        wtr = csv.DictWriter(f, fieldnames=WINDOW_FIELDS)
        wtr.writeheader()
        wtr.writerows(rows)


def _write_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def build() -> dict:
    os.makedirs(DB_DIR, exist_ok=True)
    rows = list(_rows())
    clean = [r for r in rows if _is_action(r)]

    videos = {d["video_id"]: {
        "video_id": d["video_id"], "video_url": d["url"], "title": d["title"],
        "duration_s": d["duration"], "source": d.get("source", "storyboard"),
        "n_windows": len(d["windows"]), "n_segments": len(d["segments"]),
    } for d in _timelines()}

    _write_csv(os.path.join(DB_DIR, "classifications.csv"), rows)
    _write_jsonl(os.path.join(DB_DIR, "classifications.jsonl"), rows)
    _write_csv(os.path.join(DB_DIR, "classifications_clean.csv"), clean)
    _write_jsonl(os.path.join(DB_DIR, "classifications_clean.jsonl"), clean)

    dbp = os.path.join(DB_DIR, "classifications.sqlite")
    if os.path.exists(dbp):
        os.remove(dbp)
    con = sqlite3.connect(dbp)
    cur = con.cursor()
    cur.execute("""CREATE TABLE videos(
        video_id TEXT PRIMARY KEY, video_url TEXT, title TEXT,
        duration_s REAL, source TEXT, n_windows INT, n_segments INT)""")

    def coltype(c):
        if c in ("window_index", "is_step", "has_caption", "keep"):
            return "INTEGER"
        if c.endswith("_s") or c in ("confidence", "face_score", "text_score",
                                     "motion", "brightness", "colorfulness"):
            return "REAL"
        return "TEXT"
    cols = ", ".join(f"{c} {coltype(c)}" for c in WINDOW_FIELDS)
    cur.execute(f"CREATE TABLE windows({cols}, "
                "FOREIGN KEY(video_id) REFERENCES videos(video_id))")
    cur.executemany("INSERT INTO videos VALUES (?,?,?,?,?,?,?)",
                    [(v["video_id"], v["video_url"], v["title"], v["duration_s"],
                      v["source"], v["n_windows"], v["n_segments"]) for v in videos.values()])
    cur.executemany(f"INSERT INTO windows VALUES ({','.join('?' * len(WINDOW_FIELDS))})",
                    [tuple(r[c] for c in WINDOW_FIELDS) for r in rows])
    cur.execute("CREATE INDEX idx_label ON windows(action_label)")
    cur.execute("CREATE INDEX idx_video ON windows(video_id)")
    cur.execute("CREATE INDEX idx_keep ON windows(keep)")
    cur.execute("CREATE VIEW windows_clean AS SELECT * FROM windows WHERE keep=1 AND is_step=1")
    con.commit()
    con.close()

    from collections import Counter
    reasons = Counter(r["filter_reason"] for r in rows if not r["keep"])
    return {"videos": len(videos), "windows": len(rows), "clean_windows": len(clean),
            "filtered": dict(reasons),
            "flagged": sum(1 for r in rows if r["validation_flags"]), "dir": DB_DIR}


# ---------------------------------------------------------------------------
# Split the monolithic database into per-label shards
# ---------------------------------------------------------------------------
# The full database (classifications.jsonl) is a single multi-megabyte file, so
# loading it just to look at one action is wasteful and can blow request size
# limits. `split_by_label` fans it out into outputs/db/by_label/<label>.{jsonl,csv}
# (one small file per action_label) plus an index.json manifest, so a single
# label can be read on its own. It reads the already-built db files, so it works
# without the (gitignored, regenerable) data/work intermediates.
BY_LABEL_DIR = os.path.join(DB_DIR, "by_label")


def _read_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def _safe_label(label: str) -> str:
    # action labels are already filename-safe (e.g. add_dye_color); guard anyway.
    safe = "".join(c if (c.isalnum() or c in "-_") else "_" for c in (label or "unlabeled"))
    return safe or "unlabeled"


def split_by_label() -> dict:
    """Fan the built database out into one file per action label.

    Writes, under outputs/db/by_label/:
      <label>.jsonl / <label>.csv            every window with that label (full db)
      clean/<label>.jsonl / clean/<label>.csv  the action-only subset for that label
      index.json                              manifest: per-label row counts + byte sizes
    """
    full = _read_jsonl(os.path.join(DB_DIR, "classifications.jsonl"))
    clean = _read_jsonl(os.path.join(DB_DIR, "classifications_clean.jsonl"))
    if not full:
        raise FileNotFoundError(
            "outputs/db/classifications.jsonl not found - run `ytclip build-db` first")

    clean_dir = os.path.join(BY_LABEL_DIR, "clean")
    os.makedirs(clean_dir, exist_ok=True)

    def _group(rows):
        groups: dict[str, list] = {}
        for r in rows:
            groups.setdefault(_safe_label(r.get("action_label")), []).append(r)
        return groups

    full_groups = _group(full)
    clean_groups = _group(clean)

    index: dict[str, dict] = {}
    for label, rows in sorted(full_groups.items()):
        jp = os.path.join(BY_LABEL_DIR, f"{label}.jsonl")
        cp = os.path.join(BY_LABEL_DIR, f"{label}.csv")
        _write_jsonl(jp, rows)
        _write_csv(cp, rows)
        index[label] = {
            "rows": len(rows),
            "clean_rows": len(clean_groups.get(label, [])),
            "jsonl": os.path.relpath(jp, DB_DIR),
            "csv": os.path.relpath(cp, DB_DIR),
            "bytes": os.path.getsize(jp),
        }

    for label, rows in sorted(clean_groups.items()):
        _write_jsonl(os.path.join(clean_dir, f"{label}.jsonl"), rows)
        _write_csv(os.path.join(clean_dir, f"{label}.csv"), rows)

    manifest = {
        "source": "outputs/db/classifications.jsonl",
        "total_rows": len(full),
        "total_clean_rows": len(clean),
        "n_labels": len(index),
        "labels": index,
    }
    with open(os.path.join(BY_LABEL_DIR, "index.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    return {"dir": BY_LABEL_DIR, "n_labels": len(index),
            "total_rows": len(full), "total_clean_rows": len(clean),
            "labels": {k: v["rows"] for k, v in index.items()}}
