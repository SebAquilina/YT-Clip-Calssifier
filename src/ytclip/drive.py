"""Bridge between the local shared store and its canonical Google Drive copy.

Why a bridge and not a client: this code can't call the Drive API directly (it has
no credentials) — the *Claude session* moves bytes using the Drive MCP tools
(`create_file`, `search_files`, `download_file_content`). These helpers are the
pure-Python glue around those calls: they decide what to push, decode what was
pulled, and apply newest-wins on import. The unit of sync is one record per video
(`records/<video_id>.json`), so concurrent contributors never collide.

Records are synced gzipped (`<video_id>.json.gz`): ~13x smaller than the raw
JSON, and gzip's CRC32 detects any transfer corruption on decompress, so a bad
upload can never land as silently-wrong data.

Typical loop a session runs (MCP calls in CAPS):
  pull : SEARCH_FILES(parentId=records_folder) -> for each new title
         DOWNLOAD_FILE_CONTENT -> `decode()` (gunzips) -> import -> `db-rebuild`
  push : for each r in `records_to_push(remote_titles)`
         CREATE_FILE(parentId=records_folder, title=r['title'],
                     base64Content=record_gz_b64(r['video_id']),
                     contentMimeType='application/gzip',
                     disableConversionToGoogleType=true)
"""
from __future__ import annotations

import base64
import glob
import gzip
import json
import os

from . import shared_db

CONFIG_NAME = ".drive.json"
RECORD_MIME = "application/json"
RECORD_GZ_MIME = "application/gzip"
GZIP_MAGIC = b"\x1f\x8b"


def config(root: str | None = None) -> dict:
    """Drive folder ids/urls for this store (records live under records_folder_id)."""
    p = os.path.join(shared_db._root(root), CONFIG_NAME)
    return json.load(open(p)) if os.path.exists(p) else {}


def local_records(root: str | None = None) -> list:
    """Every local record that could be pushed to Drive (as gzipped <id>.json.gz)."""
    root = shared_db._root(root)
    out = []
    for p in sorted(glob.glob(os.path.join(root, "records", "*.json"))):
        vid = os.path.basename(p)[:-5]
        raw = os.path.getsize(p)
        gz = len(gzip.compress(open(p, "rb").read()))
        out.append({"video_id": vid, "title": f"{vid}.json.gz", "path": p,
                    "size": raw, "gz_size": gz})
    return out


def records_to_push(remote_titles, root: str | None = None) -> list:
    """Local records whose `<id>.json.gz` is not already on Drive (push set).

    `remote_titles` is the set of file titles the session saw via search_files.
    Records are uploaded gzipped: ~13x smaller, and gzip's CRC catches any
    transfer corruption on decompress.
    """
    remote = set(remote_titles or [])
    return [r for r in local_records(root) if r["title"] not in remote]


def record_text(video_id: str, root: str | None = None) -> str:
    """The exact JSON text of a record (uncompressed)."""
    return open(shared_db.record_path(video_id, root)).read()


def record_gz_b64(video_id: str, root: str | None = None) -> str:
    """base64(gzip(record)) — the small, CRC-protected payload to upload.

    Upload with contentMimeType='application/gzip', disableConversionToGoogleType
    true, title='<video_id>.json.gz'.
    """
    raw = open(shared_db.record_path(video_id, root), "rb").read()
    return base64.b64encode(gzip.compress(raw)).decode("ascii")


def decode(content: str) -> str:
    """Decode a base64 payload from download_file_content to record JSON text.

    Transparently gunzips gzipped (`.json.gz`) payloads.
    """
    raw = base64.b64decode(content)
    if raw[:2] == GZIP_MAGIC:
        raw = gzip.decompress(raw)
    return raw.decode("utf-8")


def import_downloaded(items, root: str | None = None, force: bool = False) -> dict:
    """Apply records pulled from Drive (newest-wins per video).

    `items` is a list of dicts, each carrying the record as `text`, or base64
    `content` (as returned by download_file_content), or a local `path`.
    """
    added = updated = skipped = bad = 0
    for it in items:
        # A corrupt download (truncated/garbled gzip, invalid JSON) must never
        # poison the store: gzip's CRC and json parsing reject it and we skip.
        try:
            if it.get("text") is not None:
                text = it["text"]
            elif it.get("content") is not None:
                text = decode(it["content"])
            elif it.get("path"):
                raw = open(it["path"], "rb").read()
                text = (gzip.decompress(raw) if raw[:2] == GZIP_MAGIC else raw).decode("utf-8")
            else:
                continue
            vid = json.loads(text)["video_id"]
        except (OSError, ValueError, KeyError):
            bad += 1
            continue
        existed = shared_db.is_ingested(vid, root)
        res = shared_db.import_record(text, root=root, force=force)
        if res.get("skipped"):
            skipped += 1
        elif existed:
            updated += 1
        else:
            added += 1
    return {"added": added, "updated": updated, "skipped": skipped, "bad": bad}


def import_dir(directory: str, root: str | None = None, force: bool = False) -> dict:
    """Import a folder of downloaded records (.json or .json.gz), then rebuild views."""
    paths = sorted(glob.glob(os.path.join(directory, "*.json"))
                   + glob.glob(os.path.join(directory, "*.json.gz")))
    res = import_downloaded([{"path": p} for p in paths], root=root, force=force)
    res["rebuilt"] = shared_db.rebuild_views(root)["videos"]
    return res
