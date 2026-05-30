# Google Drive sync for the shared clip store

The **canonical** copy of the shared store lives in Google Drive. Each Claude
session keeps a local working copy under `outputs/shared_db/` and syncs records
to/from Drive using the **Drive MCP tools** (`search_files`, `create_file`,
`download_file_content`). The `ytclip.drive` helpers are the pure-Python glue
around those calls.

## Canonical location

| folder | id |
|---|---|
| `yt-clip-shared/` (store root) | `17cphKDGymGAt0rHjpCHQ9wXhegOD0LfG` |
| `yt-clip-shared/records/` (one JSON per video) | `1_gB7b1SI1ZBnkj_1_X93FyapH2N0FaND` |

These ids are also stored in `outputs/shared_db/.drive.json` and surfaced by
`ytclip drive-status`.

## The unit of sync: one record per video

`records/<video_id>.json` is self-contained (windows + metadata + flags). Because
every record is uniquely named:

- two sessions adding two different videos write **different files** — no
  collisions;
- a session re-uploading the same video just creates a newer version, and the
  importer keeps the one with the newest `ingested_at` (**newest wins**);
- there is no in-place edit and no shared index to corrupt.

Upload records as `contentMimeType: application/json` with
`disableConversionToGoogleType: true` so Drive stores raw JSON (not a Google Doc).

## Pull (before researching / before assembling)

1. `search_files` with `parentId = '1_gB7b1SI1ZBnkj_1_X93FyapH2N0FaND'` → list of
   `{id, title}` in `records/`.
2. For each record you don't have locally (or that's newer), `download_file_content(fileId)`
   → base64 → write the decoded JSON to `outputs/shared_db/records/<title>`.
3. `ytclip drive-import-dir <dir>` (or just drop files into `records/` and run
   `ytclip db-rebuild`) to apply newest-wins and rebuild the derived views.

## Push (after ingesting your videos)

1. `ytclip drive-push-plan --have <titles from step-1 search>` → prints the exact
   `create_file` calls (title, parentId, mime) for records not yet on Drive.
2. For each, `create_file(parentId='1_gB7b1SI1ZBnkj_1_X93FyapH2N0FaND',
   title='<video_id>.json', textContent=<file contents>,
   contentMimeType='application/json', disableConversionToGoogleType=true)`.
3. Optionally refresh the store-root `index.json` snapshot the same way.

## Why this is concurrency-safe

The only writes are **whole-file uploads of uniquely-named per-video records**.
Two sessions never write the same file unless they processed the same video, and
in that case the newest record wins on import — no lost data, no torn writes, no
lock needed. Round-trip verified: a JSON file uploaded via `create_file` and
fetched via `download_file_content` decodes back byte-for-byte.

## Verified live (2026-05-30)

- Folder tree `yt-clip-shared/` + `records/` created (ids above).
- `index.json` and a full real record `records/lTMszYRbm84.json` (22 windows)
  uploaded as `application/json` (conversion disabled) and confirmed to download
  back intact.
- The newest-wins design was exercised for real: a same-title record uploaded
  twice leaves two files on Drive, and import keeps the one with the newer
  `ingested_at`. (The Drive MCP exposes no delete tool, so redundant older
  copies are simply ignored on import; remove them in the Drive UI if desired.)
- Remaining seed records (`BbGnbTIz7_s`, `HPD1k0lhDCU`) live in the git repo and
  upload on the first `drive-push-plan` run.
