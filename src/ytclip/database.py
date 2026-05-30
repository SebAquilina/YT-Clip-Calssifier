"""Build the consolidated classification database from finalized timelines.

Reads every outputs/<id>.timeline.json and emits, in outputs/db/:
  classifications.sqlite   - two tables: videos, windows
  classifications.csv      - one row per 5-10s window (flat, spreadsheet-friendly)
  classifications.jsonl    - one JSON object per window

Each window row includes the video link plus a timestamped deep-link to the
exact moment (https://youtu.be/<id>?t=<start>s) and the detailed description.
"""
from __future__ import annotations

import csv
import glob
import json
import os
import sqlite3

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs"))
DB_DIR = os.path.join(OUT, "db")

WINDOW_FIELDS = [
    "video_id", "video_url", "video_title", "video_duration_s", "source",
    "window_index", "start_s", "end_s", "duration_s", "window_url",
    "action_label", "phase", "is_step", "confidence", "description",
]


def _timelines():
    for p in sorted(glob.glob(os.path.join(OUT, "*.timeline.json"))):
        with open(p) as f:
            yield json.load(f)


def _rows():
    for d in _timelines():
        vid, url = d["video_id"], d["url"]
        for w in d["windows"]:
            start = int(round(w["start"]))
            yield {
                "video_id": vid,
                "video_url": url,
                "video_title": d["title"],
                "video_duration_s": d["duration"],
                "source": d.get("source", "storyboard"),
                "window_index": w["window"],
                "start_s": w["start"],
                "end_s": w["end"],
                "duration_s": round(w["end"] - w["start"], 2),
                "window_url": f"https://youtu.be/{vid}?t={start}s",
                "action_label": w["label"],
                "phase": w.get("phase", ""),
                "is_step": int(bool(w.get("is_step"))),
                "confidence": w.get("confidence", 0.0),
                "description": w.get("description") or w.get("evidence", ""),
            }


def build() -> dict:
    os.makedirs(DB_DIR, exist_ok=True)
    rows = list(_rows())
    videos = {}
    for d in _timelines():
        videos[d["video_id"]] = {
            "video_id": d["video_id"], "video_url": d["url"], "title": d["title"],
            "duration_s": d["duration"], "source": d.get("source", "storyboard"),
            "n_windows": len(d["windows"]), "n_segments": len(d["segments"]),
        }

    # CSV
    with open(os.path.join(DB_DIR, "classifications.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=WINDOW_FIELDS)
        w.writeheader()
        w.writerows(rows)

    # JSONL
    with open(os.path.join(DB_DIR, "classifications.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    # SQLite
    dbp = os.path.join(DB_DIR, "classifications.sqlite")
    if os.path.exists(dbp):
        os.remove(dbp)
    con = sqlite3.connect(dbp)
    cur = con.cursor()
    cur.execute("""CREATE TABLE videos(
        video_id TEXT PRIMARY KEY, video_url TEXT, title TEXT,
        duration_s REAL, source TEXT, n_windows INT, n_segments INT)""")
    cur.execute(f"""CREATE TABLE windows(
        {', '.join(f'{c} {"INTEGER" if c in ("window_index","is_step") else "REAL" if c.endswith("_s") or c=="confidence" else "TEXT"}' for c in WINDOW_FIELDS)},
        FOREIGN KEY(video_id) REFERENCES videos(video_id))""")
    cur.executemany(
        "INSERT INTO videos VALUES (?,?,?,?,?,?,?)",
        [(v["video_id"], v["video_url"], v["title"], v["duration_s"], v["source"],
          v["n_windows"], v["n_segments"]) for v in videos.values()])
    cur.executemany(
        f"INSERT INTO windows VALUES ({','.join('?' * len(WINDOW_FIELDS))})",
        [tuple(r[c] for c in WINDOW_FIELDS) for r in rows])
    cur.execute("CREATE INDEX idx_label ON windows(action_label)")
    cur.execute("CREATE INDEX idx_video ON windows(video_id)")
    con.commit()
    con.close()

    return {"videos": len(videos), "windows": len(rows), "dir": DB_DIR}
