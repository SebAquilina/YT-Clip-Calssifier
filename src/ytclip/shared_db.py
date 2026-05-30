"""Concurrency-safe, label-sharded shared clip database for cross-chat use.

Goal: many Claude sessions ("coworker chats") can ingest videos into ONE shared
store at the same time without corrupting it, and a video-making run can read
back vetted, non-flagged clips for a niche.

Design — shard by (label, video_id) so writers never collide
------------------------------------------------------------
    <root>/
      by_label/<label>/<video_id>.jsonl   every window of that video+label
      by_label/<label>.jsonl              REBUILDABLE merged view (not source)
      flags/<video_id>.json               windows to NEVER use as footage
      _index/<video_id>.json              "this video is done" marker + metadata
      index.json                          rebuilt manifest (counts per label/video)

Because every file is named by a unique video_id, two chats processing two
different videos touch disjoint files -> no locks needed, no lost writes. A chat
that re-processes an already-ingested video is a no-op (idempotent) unless it
passes force=True. Every individual file is written atomically (tmp + os.replace),
and the `_index/<video_id>.json` marker is written LAST, so a video is only
"seen" once all its shards are safely on disk.

The merged `by_label/<label>.jsonl` views and `index.json` are read-side
aggregations rebuilt from the shards by `rebuild_views()`; they are never the
source of truth, so rebuilding them can't corrupt ingested data.
"""
from __future__ import annotations

import glob
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


def is_ingested(video_id: str, root: str | None = None) -> bool:
    return os.path.exists(os.path.join(_root(root), "_index", f"{_safe(video_id)}.json"))


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


def ingest_rows(video_id: str, rows: list, meta: dict | None = None,
                root: str | None = None, force: bool = False) -> dict:
    """Add ONE video's classified windows to the shared store (concurrency-safe).

    Writes per-(label) shards for this video, a flags file listing the
    never-use windows, and a final _index marker. Idempotent: a video already
    in the store is skipped unless force=True.
    """
    root = _root(root)
    vid = _safe(video_id)
    if is_ingested(video_id, root) and not force:
        return {"video_id": video_id, "skipped": True, "reason": "already ingested"}
    if not rows:
        raise ValueError(f"no rows to ingest for {video_id}")

    # group this video's windows by label and write one shard per label
    by_label: dict[str, list] = {}
    for r in rows:
        by_label.setdefault(_safe(r.get("action_label", "unlabeled")), []).append(r)
    for label, lrows in by_label.items():
        path = os.path.join(root, "by_label", label, f"{vid}.jsonl")
        _atomic_write(path, "".join(json.dumps(r) + "\n" for r in lrows))

    # flags = windows that must never be used as footage (talking head / text / non-action)
    flags = []
    for r in rows:
        reason = _flag_reason(r)
        if reason:
            flags.append({"window_index": r.get("window_index"),
                          "start_s": r.get("start_s"), "end_s": r.get("end_s"),
                          "action_label": r.get("action_label"), "reason": reason})
    usable = len(rows) - len(flags)
    _atomic_write(os.path.join(root, "flags", f"{vid}.json"),
                  json.dumps({"video_id": video_id, "flagged": flags}, indent=1))

    # _index marker written LAST: a video only "counts" once its shards are on disk
    m = dict(meta or {})
    first = rows[0]
    index = {
        "video_id": video_id,
        "video_title": m.get("video_title", first.get("video_title", "")),
        "video_url": m.get("video_url", first.get("video_url", "")),
        "video_duration_s": m.get("video_duration_s", first.get("video_duration_s")),
        "source": m.get("source", first.get("source", "")),
        "niche": m.get("niche", ""),
        "n_windows": len(rows),
        "n_usable": usable,
        "n_flagged": len(flags),
        "labels": {lbl: len(lr) for lbl, lr in sorted(by_label.items())},
        "ingested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _atomic_write(os.path.join(root, "_index", f"{vid}.json"), json.dumps(index, indent=1))
    return {"video_id": video_id, "skipped": False,
            "n_windows": len(rows), "n_usable": usable, "n_flagged": len(flags),
            "labels": index["labels"]}


def ingest_video(video_id: str, root: str | None = None, force: bool = False,
                 meta: dict | None = None) -> dict:
    """Ingest a finalized video by reading its timeline (+features) from outputs/."""
    from .database import rows_for_video
    return ingest_rows(video_id, rows_for_video(video_id), meta=meta, root=root, force=force)


def flagged_windows(video_id: str, root: str | None = None) -> list:
    p = os.path.join(_root(root), "flags", f"{_safe(video_id)}.json")
    if not os.path.exists(p):
        return []
    return json.load(open(p)).get("flagged", [])


def is_flagged(video_id: str, window_index: int, root: str | None = None) -> bool:
    """Second-layer check: is this specific window unusable as footage?"""
    return any(f.get("window_index") == window_index
               for f in flagged_windows(video_id, root))


def usable_clips(label: str | None = None, niche: str | None = None,
                 root: str | None = None) -> list:
    """Return clean action clips (keep & is_step, not flagged), optionally by label.

    Double-checked: rows come from action-label shards AND are re-verified against
    each video's flags file before being returned.
    """
    root = _root(root)
    labels = [label] if label else _action_labels(root)
    niche_ids = None
    if niche:
        niche_ids = {ix["video_id"] for ix in _indexes(root) if ix.get("niche") == niche}
    out = []
    for lbl in labels:
        for shard in glob.glob(os.path.join(root, "by_label", _safe(lbl), "*.jsonl")):
            for line in open(shard):
                if not line.strip():
                    continue
                r = json.loads(line)
                if niche_ids is not None and r.get("video_id") not in niche_ids:
                    continue
                if _flag_reason(r) is None and not is_flagged(
                        r.get("video_id"), r.get("window_index"), root):
                    out.append(r)
    return out


def _action_labels(root: str) -> list:
    base = os.path.join(root, "by_label")
    if not os.path.isdir(base):
        return []
    return [d for d in os.listdir(base)
            if os.path.isdir(os.path.join(base, d)) and d not in _NON_FOOTAGE_LABELS]


def _indexes(root: str) -> list:
    return [json.load(open(p))
            for p in glob.glob(os.path.join(root, "_index", "*.json"))]


def rebuild_views(root: str | None = None) -> dict:
    """Rebuild the merged by_label/<label>.jsonl views + index.json from the shards."""
    root = _root(root)
    base = os.path.join(root, "by_label")
    labels = {}
    if os.path.isdir(base):
        for label in sorted(os.listdir(base)):
            ldir = os.path.join(base, label)
            if not os.path.isdir(ldir):
                continue
            shards = sorted(glob.glob(os.path.join(ldir, "*.jsonl")))
            lines, n = [], 0
            for s in shards:
                for line in open(s):
                    if line.strip():
                        lines.append(line if line.endswith("\n") else line + "\n")
                        n += 1
            _atomic_write(os.path.join(base, f"{label}.jsonl"), "".join(lines))
            labels[label] = {"videos": len(shards), "windows": n}

    idx = _indexes(root)
    manifest = {
        "videos": len(idx),
        "windows": sum(i.get("n_windows", 0) for i in idx),
        "usable": sum(i.get("n_usable", 0) for i in idx),
        "flagged": sum(i.get("n_flagged", 0) for i in idx),
        "labels": labels,
        "niches": sorted({i.get("niche", "") for i in idx if i.get("niche")}),
        "video_ids": sorted(i["video_id"] for i in idx),
        "rebuilt_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _atomic_write(os.path.join(root, "index.json"), json.dumps(manifest, indent=1))
    return manifest


def stats(root: str | None = None) -> dict:
    idx = _indexes(_root(root))
    return {
        "videos": len(idx),
        "windows": sum(i.get("n_windows", 0) for i in idx),
        "usable": sum(i.get("n_usable", 0) for i in idx),
        "flagged": sum(i.get("n_flagged", 0) for i in idx),
        "niches": sorted({i.get("niche", "") for i in idx if i.get("niche")}),
    }
