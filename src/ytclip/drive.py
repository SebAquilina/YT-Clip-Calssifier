"""Bridge between the local shared store and its canonical Google Drive copy.

Why a bridge and not a client: this code can't call the Drive API directly (it has
no credentials) — the *Claude session* moves bytes using the Drive MCP tools
(`create_file`, `search_files`, `download_file_content`). These helpers are the
pure-Python glue around those calls: they decide what to push, decode what was
pulled, and apply newest-wins on import. The unit of sync is one record per video
(`records/<video_id>.json`), so concurrent contributors never collide.

Typical loop a session runs (MCP calls in CAPS):
  pull : SEARCH_FILES(parentId=records_folder) -> for each new title
         DOWNLOAD_FILE_CONTENT -> write JSON into records/ -> `ytclip db-rebuild`
  push : for each path in `records_to_push(remote_titles)`
         CREATE_FILE(parentId=records_folder, title=<id>.json,
                     textContent=<file>, contentMimeType='application/json',
                     disableConversionToGoogleType=true)
"""
from __future__ import annotations

import base64
import glob
import json
import os

from . import shared_db

CONFIG_NAME = ".drive.json"
RECORD_MIME = "application/json"


def config(root: str | None = None) -> dict:
    """Drive folder ids/urls for this store (records live under records_folder_id)."""
    p = os.path.join(shared_db._root(root), CONFIG_NAME)
    return json.load(open(p)) if os.path.exists(p) else {}


def local_records(root: str | None = None) -> list:
    """Every local record that could be pushed to Drive."""
    root = shared_db._root(root)
    out = []
    for p in sorted(glob.glob(os.path.join(root, "records", "*.json"))):
        out.append({"video_id": os.path.basename(p)[:-5],
                    "title": os.path.basename(p), "path": p,
                    "size": os.path.getsize(p)})
    return out


def records_to_push(remote_titles, root: str | None = None) -> list:
    """Local records whose `<id>.json` is not already on Drive (push set).

    `remote_titles` is the set of file titles the session saw via search_files.
    """
    remote = set(remote_titles or [])
    return [r for r in local_records(root) if r["title"] not in remote]


def record_text(video_id: str, root: str | None = None) -> str:
    """The exact text to upload for one video (create_file textContent)."""
    return open(shared_db.record_path(video_id, root)).read()


def decode(content: str) -> str:
    """Decode the base64 string returned by download_file_content to text."""
    return base64.b64decode(content).decode("utf-8")


def import_downloaded(items, root: str | None = None, force: bool = False) -> dict:
    """Apply records pulled from Drive (newest-wins per video).

    `items` is a list of dicts, each carrying the record as `text`, or base64
    `content` (as returned by download_file_content), or a local `path`.
    """
    added = updated = skipped = 0
    for it in items:
        if it.get("text") is not None:
            text = it["text"]
        elif it.get("content") is not None:
            text = decode(it["content"])
        elif it.get("path"):
            text = open(it["path"]).read()
        else:
            continue
        existed = shared_db.is_ingested(json.loads(text)["video_id"], root)
        res = shared_db.import_record(text, root=root, force=force)
        if res.get("skipped"):
            skipped += 1
        elif existed:
            updated += 1
        else:
            added += 1
    return {"added": added, "updated": updated, "skipped": skipped}


def import_dir(directory: str, root: str | None = None, force: bool = False) -> dict:
    """Import a folder of downloaded record JSON files, then rebuild local views."""
    items = [{"path": p} for p in sorted(glob.glob(os.path.join(directory, "*.json")))]
    res = import_downloaded(items, root=root, force=force)
    res["rebuilt"] = shared_db.rebuild_views(root)["videos"]
    return res
