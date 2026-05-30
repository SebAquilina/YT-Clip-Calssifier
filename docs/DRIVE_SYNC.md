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

## The unit of sync: one gzipped record per video

`records/<video_id>.json.gz` holds the gzip of a self-contained record (windows +
metadata + flags). Because every record is uniquely named:

- two sessions adding two different videos write **different files** — no
  collisions;
- a session re-uploading the same video just creates a newer version, and the
  importer keeps the one with the newest `ingested_at` (**newest wins**);
- there is no in-place edit and no shared index to corrupt.

**Why gzip:** records can be 50–70 KB+ of JSON; gzipped they are ~3–5 KB, which
is small enough to move through a tool call reliably, and **gzip's CRC32 means a
truncated or garbled transfer is rejected on decompress** rather than landing as
silently-wrong data. `drive.decode()` gunzips transparently; `import_downloaded`
**skips** (counts as `bad`) any payload that fails to decompress or parse, so a
corrupt upload can never poison the store.

Upload with `contentMimeType: application/gzip`,
`disableConversionToGoogleType: true`, `base64Content = gzip(record)`. After each
upload, verify `get_file_metadata.fileSize` equals the local gz byte count — an
exact match confirms an intact transfer.

## Pull (before researching / before assembling)

1. `search_files` with `parentId = '1_gB7b1SI1ZBnkj_1_X93FyapH2N0FaND'` → list of
   `{id, title}` in `records/`.
2. For each `<id>.json.gz` you don't have locally, `download_file_content(fileId)`
   → write the base64-decoded bytes to `outputs/shared_db/records/<title>`.
3. `ytclip drive-import-dir <dir>` (or drop the `.json.gz` files into `records/`
   and run `ytclip db-rebuild`) to gunzip, apply newest-wins, skip any corrupt
   payloads, and rebuild the derived views.

## Push (after ingesting your videos)

1. `ytclip drive-push-plan --have <titles from step-1 search>` → prints the exact
   `create_file` calls for records not yet on Drive (gzipped, with sizes).
2. For each, `create_file(parentId='1_gB7b1SI1ZBnkj_1_X93FyapH2N0FaND',
   title='<video_id>.json.gz', base64Content=$(gzip -c <path> | base64 -w0),
   contentMimeType='application/gzip', disableConversionToGoogleType=true)`, then
   confirm `get_file_metadata.fileSize` matches the local gz size.
3. Optionally refresh the store-root `index.json` snapshot the same way.

## Why this is concurrency-safe

The only writes are **whole-file uploads of uniquely-named per-video records**.
Two sessions never write the same file unless they processed the same video, and
in that case the newest record wins on import — no lost data, no torn writes, no
lock needed. Round-trip verified: a JSON file uploaded via `create_file` and
fetched via `download_file_content` decodes back byte-for-byte.

## Verified live (2026-05-30)

- Folder tree `yt-clip-shared/` + `records/` created (ids above).
- **All three seed records uploaded as gzip and verified by exact byte-size
  match:** `lTMszYRbm84.json.gz` (2135 B), `BbGnbTIz7_s.json.gz` (4249 B),
  `HPD1k0lhDCU.json.gz` (3805 B); plus the store-root `index.json` snapshot.
- The integrity guard proved itself in practice: a first hand-transcribed upload
  of the largest record came out the wrong size (caught immediately by the size
  check), was re-uploaded correctly, and the importer is hardened to skip any
  bad payload regardless.
- The Drive MCP exposes **no delete tool**, so a few redundant older copies
  remain (an early plain-JSON `lTMszYRbm84.json`, a partial duplicate, and one
  wrong-size `HPD1k0lhDCU.json.gz`). All are harmless — import takes the newest
  valid record per video and ignores corrupt/older ones — but you can delete
  them in the Drive UI to tidy up.
