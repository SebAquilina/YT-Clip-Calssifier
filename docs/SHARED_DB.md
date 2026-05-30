# Shared cross-chat clip database

A single, growing, label-organised store of categorised YouTube clips that many
Claude sessions ("coworker chats") can **read and extend at the same time**
without corrupting each other. It is the backing store for the
`YTA-video-maker` workflow: research a niche once, reuse the vetted clips across
every future video in that niche.

## Why it is safe for simultaneous writers

The store **shards by `(label, video_id)`** — every file is named by a unique
video id, so two chats processing two different videos write to **disjoint
files**. No locks, no lost writes, no corruption.

```
outputs/shared_db/                       (root; lives in the chosen storage)
  by_label/<label>/<video_id>.jsonl      one video's windows for that label   ← source of truth
  by_label/<label>.jsonl                 merged view, REBUILDABLE              ← derived
  flags/<video_id>.json                  windows to NEVER use as footage
  _index/<video_id>.json                 "done" marker + per-video metadata
  index.json                             rebuilt manifest                      ← derived
```

Guarantees:

- **Atomic files** — every write goes to a temp file then `os.replace()`, so a
  reader never sees a half-written file.
- **Commit marker last** — `_index/<video_id>.json` is written *after* all of a
  video's shards, so a video only "counts" once its data is fully on disk.
- **Idempotent** — re-ingesting an already-present video is a no-op unless
  `force=True`; the same video is never double-counted.
- **Derived views can't corrupt data** — `by_label/<label>.jsonl` and
  `index.json` are rebuilt from the shards by `rebuild_views()`; they are never
  the source of truth.

> Concurrency is covered by `tests/test_shared_db.py`, which ingests 40 videos
> across 8 threads and asserts the merged views are lossless with exactly one
> entry per video.

## Flags — the double layer against bad footage

On ingest, every window that is **not a clean hands-on action clip** is recorded
in `flags/<video_id>.json` with a reason (`talking_head`, `text_overlay`,
`blank`, `non_action:<label>`, …). Footage selection is then checked twice:

1. `usable_clips()` only reads the **action-label** shards (it skips
   `talking_head`, `intro_titlecard`, `outro_cta`, `transition`, `blank`,
   `other_unclear` entirely), and
2. it re-verifies every candidate against that video's flags file
   (`is_flagged(video_id, window_index)`) before returning it.

So a talking-head or on-screen-text window cannot reach the final cut even if a
label were wrong.

## CLI

```bash
ytclip db-ingest <video_id> --niche candle_making   # add a finalized video to the store
ytclip db-rebuild                                   # rebuild merged views + index.json
ytclip db-stats                                     # summarise the store
```

Programmatic API lives in `ytclip.shared_db`: `ingest_video`, `ingest_rows`,
`usable_clips`, `flagged_windows`, `is_flagged`, `is_ingested`, `rebuild_views`,
`stats`.

## Storage / cross-chat access

The engine is **storage-agnostic** — it operates on a directory (`SHARED_DIR`,
default `outputs/shared_db/`). To share that directory across chats:

- **Git repo (recommended for writers):** each session clones, ingests its
  videos, and commits/pushes. Per-video file naming makes merges conflict-free.
- **Drive (connected file MCP):** mirror the directory; readers/writers use the
  Drive tools.
- **claude.ai Project knowledge (read-only mirror):** Project files are *context*,
  not a transactional store — a Code session can't append to them and concurrent
  appends aren't supported. Use them for a periodically **exported snapshot** so
  Project chats can *read* the latest store; keep the writable canonical copy in
  git or Drive.

## Intended `YTA-video-maker` pipeline (skill wiring — pending the skill MD)

1. **Read first** — load the store, list which niches/videos are already covered.
2. **Targeted research** — search ~10 videos specific to *this* video type (the
   broad niche is already researched), skipping any `video_id` already ingested.
3. **Classify in-session** — `prepare` → contact sheets → Claude labels each
   5–10s window → `finalize`.
4. **Ingest** — `db-ingest <id> --niche <niche>` writes the per-label shards +
   flags + index (concurrency-safe).
5. **Select footage** — `usable_clips(niche=…)` returns vetted, non-flagged clips
   for assembly, after which the **normal video-making process + rules** run.
