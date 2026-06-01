"""Concurrency-safe shared clip database for cross-chat use, synced via Google Drive.

Goal: many Claude sessions ("coworker chats") can ingest videos into ONE shared
store at the same time without corrupting it, and a video-making run can read
back vetted, non-flagged clips for a niche.

Design — one self-contained record per video (the Drive-friendly unit)
----------------------------------------------------------------------
    <root>/
      records/<video_id>.json   SOURCE OF TRUTH: a video's windows + meta + flags
      by_label/<label>.jsonl    DERIVED, rebuildable view ("divided by label")
      flags/<video_id>.json     DERIVED, extracted for convenience
      index.json                DERIVED manifest (counts per label / niche / video)

Why per-video records: Google Drive's unit is a file, so each video maps to one
`records/<video_id>.json`. Because every record is named by a unique video id,
two chats processing two different videos write disjoint files -> no locks, no
lost writes. The same video processed twice is idempotent locally (skip unless
force); on Drive a same-title re-upload just makes a newer version, and readers
keep the newest. Every file is written atomically (tmp + os.replace).

`by_label/`, `flags/` and `index.json` are materialized from the records by
`rebuild_views()`; they are never the source of truth, so rebuilding them can't
corrupt ingested data. Queries (`usable_clips`, `coverage`, …) read the records
directly, so they are correct the instant a record lands — no rebuild required.
"""
from __future__ import annotations

import csv
import glob
import io
import json
import os
import time
import uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SHARED_DIR = os.path.join(ROOT, "outputs", "shared_db")

# Labels whose windows must never be used as B-roll footage in a cut.
# (talking-head and on-screen-text/title/transition/blank content.)
_NON_FOOTAGE_LABELS = {
    "talking_head", "intro_titlecard", "outro_cta", "transition",
    "other_unclear", "blank",
}


def _root(root: str | None) -> str:
    return root or SHARED_DIR


def _atomic_write(path: str, text: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
    with open(tmp, "w") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)          # atomic on the same filesystem


def _safe(name: str) -> str:
    return "".join(c if (c.isalnum() or c in "-_") else "_" for c in (name or "x")) or "x"


# --------------------------------------------------------------------------- #
# record layer (source of truth)                                              #
# --------------------------------------------------------------------------- #
def record_path(video_id: str, root: str | None = None) -> str:
    return os.path.join(_root(root), "records", f"{_safe(video_id)}.json")


def is_ingested(video_id: str, root: str | None = None) -> bool:
    return os.path.exists(record_path(video_id, root))


def load_record(video_id: str, root: str | None = None) -> dict | None:
    p = record_path(video_id, root)
    return json.load(open(p)) if os.path.exists(p) else None


def all_records(root: str | None = None) -> list:
    out = []
    for p in sorted(glob.glob(os.path.join(_root(root), "records", "*.json"))):
        if os.path.basename(p) == "manifest.json":   # checksum file, not a record
            continue
        try:
            rec = json.load(open(p))
        except (ValueError, OSError):
            continue
        if isinstance(rec, dict) and rec.get("video_id"):
            out.append(rec)
    return out


def _flag_reason(row: dict) -> str | None:
    """Why a window is NOT usable footage, or None if it is a clean action clip."""
    if row.get("filter_reason"):                       # detector said talking_head/text_overlay/blank
        return row["filter_reason"]
    if not int(row.get("is_step") or 0):               # not a hands-on procedure step
        lbl = row.get("action_label", "")
        return f"non_action:{lbl}" if lbl in _NON_FOOTAGE_LABELS else "non_action"
    if not int(row.get("keep", 1)):
        return "filtered"
    return None


def _build_record(video_id: str, rows: list, meta: dict | None) -> dict:
    flags = []
    for r in rows:
        reason = _flag_reason(r)
        if reason:
            flags.append({"window_index": r.get("window_index"),
                          "start_s": r.get("start_s"), "end_s": r.get("end_s"),
                          "action_label": r.get("action_label"), "reason": reason})
    m = dict(meta or {})
    first = rows[0]
    labels: dict[str, int] = {}
    for r in rows:
        labels[r.get("action_label", "unlabeled")] = labels.get(r.get("action_label", "unlabeled"), 0) + 1
    return {
        "video_id": video_id,
        "video_title": m.get("video_title", first.get("video_title", "")),
        "video_url": m.get("video_url", first.get("video_url", "")),
        "video_duration_s": m.get("video_duration_s", first.get("video_duration_s")),
        "source": m.get("source", first.get("source", "")),
        "niche": m.get("niche", ""),
        "ingested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_windows": len(rows),
        "n_usable": len(rows) - len(flags),
        "n_flagged": len(flags),
        "labels": dict(sorted(labels.items())),
        "flagged": flags,
        "windows": rows,
    }


def ingest_rows(video_id: str, rows: list, meta: dict | None = None,
                root: str | None = None, force: bool = False) -> dict:
    """Add ONE video's classified windows to the shared store (concurrency-safe).

    Writes a single self-contained `records/<video_id>.json`. Idempotent: skipped
    if the video is already present unless force=True.
    """
    if is_ingested(video_id, root) and not force:
        return {"video_id": video_id, "skipped": True, "reason": "already ingested"}
    if not rows:
        raise ValueError(f"no rows to ingest for {video_id}")
    rec = _build_record(video_id, rows, meta)
    _atomic_write(record_path(video_id, root), json.dumps(rec))
    return {"video_id": video_id, "skipped": False, "n_windows": rec["n_windows"],
            "n_usable": rec["n_usable"], "n_flagged": rec["n_flagged"], "labels": rec["labels"]}


def ingest_video(video_id: str, root: str | None = None, force: bool = False,
                 meta: dict | None = None) -> dict:
    """Ingest a finalized video by reading its timeline (+features) from outputs/."""
    from .database import rows_for_video
    return ingest_rows(video_id, rows_for_video(video_id), meta=meta, root=root, force=force)


def import_record(text_or_path: str, root: str | None = None, force: bool = False) -> dict:
    """Write a record fetched from Drive into the local store.

    `text_or_path` is the record JSON (string) or a path to it. Newest wins: an
    existing record is replaced only if the incoming `ingested_at` is newer (or
    force=True). Used when pulling other chats' contributions down from Drive.
    """
    rec = json.loads(text_or_path) if text_or_path.lstrip().startswith("{") \
        else json.load(open(text_or_path))
    vid = rec["video_id"]
    if not force:
        cur = load_record(vid, root)
        if cur and (cur.get("ingested_at") or "") >= (rec.get("ingested_at") or ""):
            return {"video_id": vid, "skipped": True, "reason": "local copy is newer/equal"}
    _atomic_write(record_path(vid, root), json.dumps(rec))
    return {"video_id": vid, "skipped": False, "n_windows": rec.get("n_windows")}


# --------------------------------------------------------------------------- #
# flags / footage selection                                                   #
# --------------------------------------------------------------------------- #
def flagged_windows(video_id: str, root: str | None = None) -> list:
    rec = load_record(video_id, root)
    return rec.get("flagged", []) if rec else []


def is_flagged(video_id: str, window_index: int, root: str | None = None) -> bool:
    """Second-layer check: is this specific window unusable as footage?"""
    return any(f.get("window_index") == window_index
               for f in flagged_windows(video_id, root))


def usable_clips(label: str | None = None, niche: str | None = None,
                 root: str | None = None, records: list | None = None) -> list:
    """Return clean action clips (keep & is_step, not flagged), optionally by label.

    Double-checked: a window must have a clean `_flag_reason` AND not appear in its
    record's flagged list. Talking-head / on-screen-text windows can never pass.
    `records` may be pre-loaded to avoid re-reading the store per call.
    """
    recs = records if records is not None else all_records(root)
    out = []
    for rec in recs:
        if niche and rec.get("niche") != niche:
            continue
        flagged_idx = {f.get("window_index") for f in rec.get("flagged", [])}
        for r in rec.get("windows", []):
            if label and r.get("action_label") != label:
                continue
            if r.get("action_label") in _NON_FOOTAGE_LABELS:
                continue
            if _flag_reason(r) is None and r.get("window_index") not in flagged_idx:
                out.append(r)
    return out


def _action_labels(root: str | None = None, records: list | None = None) -> list:
    recs = records if records is not None else all_records(root)
    labels = set()
    for rec in recs:
        for lbl in rec.get("labels", {}):
            if lbl not in _NON_FOOTAGE_LABELS:
                labels.add(lbl)
    return sorted(labels)


# --------------------------------------------------------------------------- #
# derived views + summaries                                                   #
# --------------------------------------------------------------------------- #
def _csv_text(rows: list) -> str:
    """Render rows as CSV using the canonical column order (one file per label)."""
    from .database import WINDOW_FIELDS
    buf = io.StringIO()
    wtr = csv.DictWriter(buf, fieldnames=WINDOW_FIELDS, extrasaction="ignore")
    wtr.writeheader()
    wtr.writerows(rows)
    return buf.getvalue()


def rebuild_views(root: str | None = None) -> dict:
    """Materialize the per-label views (.jsonl + .csv), flags/ and index.json from records."""
    root = _root(root)
    recs = all_records(root)

    by_label: dict[str, list] = {}
    for rec in recs:
        _atomic_write(os.path.join(root, "flags", f"{_safe(rec['video_id'])}.json"),
                      json.dumps({"video_id": rec["video_id"], "flagged": rec.get("flagged", [])}, indent=1))
        for r in rec.get("windows", []):
            by_label.setdefault(_safe(r.get("action_label", "unlabeled")), []).append(r)

    labels_manifest = {}
    base = os.path.join(root, "by_label")
    # clear stale label views then rewrite (one .jsonl + one .csv per label)
    for old in glob.glob(os.path.join(base, "*.jsonl")) + glob.glob(os.path.join(base, "*.csv")):
        os.remove(old)
    for label, lrows in sorted(by_label.items()):
        lrows.sort(key=lambda r: (r.get("video_id", ""), r.get("window_index", 0)))
        _atomic_write(os.path.join(base, f"{label}.jsonl"),
                      "".join(json.dumps(r) + "\n" for r in lrows))
        _atomic_write(os.path.join(base, f"{label}.csv"), _csv_text(lrows))
        labels_manifest[label] = len(lrows)

    manifest = {
        "videos": len(recs),
        "windows": sum(r.get("n_windows", 0) for r in recs),
        "usable": sum(r.get("n_usable", 0) for r in recs),
        "flagged": sum(r.get("n_flagged", 0) for r in recs),
        "labels": labels_manifest,
        "niches": sorted({r.get("niche", "") for r in recs if r.get("niche")}),
        "video_ids": sorted(r["video_id"] for r in recs),
        "rebuilt_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _atomic_write(os.path.join(root, "index.json"), json.dumps(manifest, indent=1))
    return manifest


def stats(root: str | None = None) -> dict:
    recs = all_records(root)
    return {
        "videos": len(recs),
        "windows": sum(r.get("n_windows", 0) for r in recs),
        "usable": sum(r.get("n_usable", 0) for r in recs),
        "flagged": sum(r.get("n_flagged", 0) for r in recs),
        "niches": sorted({r.get("niche", "") for r in recs if r.get("niche")}),
    }


def coverage(root: str | None = None) -> dict:
    """What is already in the store — so a chat reads before it researches."""
    recs = all_records(root)
    niches: dict[str, list] = {}
    for r in recs:
        niches.setdefault(r.get("niche") or "(untagged)", []).append({
            "video_id": r["video_id"], "title": r.get("video_title", ""),
            "usable": r.get("n_usable", 0), "flagged": r.get("n_flagged", 0),
        })
    labels: dict[str, int] = {}
    for lbl in _action_labels(records=recs):
        labels[lbl] = len(usable_clips(label=lbl, records=recs))
    return {
        "videos": len(recs),
        "niches": {n: sorted(v, key=lambda r: -r["usable"]) for n, v in sorted(niches.items())},
        "usable_by_label": dict(sorted(labels.items(), key=lambda kv: -kv[1])),
    }


def _video_id_from(s: str) -> str:
    """Accept a bare id or a YouTube URL and return the 11-char video id."""
    s = (s or "").strip()
    for marker in ("watch?v=", "youtu.be/", "/shorts/", "/embed/", "v="):
        if marker in s:
            s = s.split(marker, 1)[1]
            break
    for sep in ("&", "?", "/", "#"):
        s = s.split(sep, 1)[0]
    return s


def pending(candidates: list, root: str | None = None) -> dict:
    """Split candidate videos into already-covered vs still-to-research.

    Accepts bare ids or YouTube URLs. Lets a chat take ~10 candidate videos for a
    new video type and skip the ones the shared store already has.
    """
    seen, covered, todo = set(), [], []
    for c in candidates:
        vid = _video_id_from(c)
        if not vid or vid in seen:
            continue
        seen.add(vid)
        (covered if is_ingested(vid, root) else todo).append(vid)
    return {"pending": todo, "covered": covered,
            "n_pending": len(todo), "n_covered": len(covered)}
