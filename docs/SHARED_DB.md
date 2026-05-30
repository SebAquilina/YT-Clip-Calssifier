# Shared cross-chat clip database

A single, growing, label-organised store of categorised YouTube clips that many
Claude sessions ("coworker chats") can **read and extend at the same time**
without corrupting each other. It is the backing store for the
`YTA-video-maker` workflow: research a niche once, reuse the vetted clips across
every future video in that niche.

## Why it is safe for simultaneous writers

The source of truth is **one self-contained record per video**
(`records/<video_id>.json`) — every record is named by a unique video id, so two
chats processing two different videos write **disjoint files**. No locks, no lost
writes, no corruption. This is also the natural **Google Drive** unit (one
file per video; see [`DRIVE_SYNC.md`](DRIVE_SYNC.md)).

```
outputs/shared_db/                  (root; canonical copy on Google Drive)
  records/<video_id>.json           a video's windows + meta + flags   ← SOURCE OF TRUTH
  by_label/<label>.jsonl            "divided by label" view            ← derived, rebuildable
  flags/<video_id>.json             windows to NEVER use as footage    ← derived
  index.json                        manifest (counts per label/niche)  ← derived
  .drive.json                       canonical Drive folder ids
```

Guarantees:

- **Atomic files** — every write goes to a temp file then `os.replace()`, so a
  reader never sees a half-written file.
- **Idempotent** — re-ingesting an already-present video is a no-op unless
  `force=True`; the same video is never double-counted. On import from Drive,
  **newest `ingested_at` wins**.
- **Queries read the source** — `usable_clips`, `coverage`, etc. read the records
  directly, so they're correct the instant a record lands; no rebuild needed.
- **Derived views can't corrupt data** — `by_label/<label>.jsonl`, `flags/` and
  `index.json` are materialized from the records by `rebuild_views()`; they are
  never the source of truth.

> Concurrency is covered by `tests/test_shared_db.py`, which ingests 40 videos
> across 8 threads and asserts the materialized views are lossless with exactly
> one entry per video.

## Flags — the double layer against bad footage

On ingest, every window that is **not a clean hands-on action clip** is recorded
in the record's `flagged` list with a reason (`talking_head`, `text_overlay`,
`blank`, `non_action:<label>`, …); it is also materialized to
`flags/<video_id>.json`. Footage selection is then checked twice:

1. `usable_clips()` skips the non-footage labels entirely (`talking_head`,
   `intro_titlecard`, `outro_cta`, `transition`, `blank`, `other_unclear`), and
2. it re-verifies every candidate against that video's flagged list
   (`is_flagged(video_id, window_index)`) before returning it.

So a talking-head or on-screen-text window cannot reach the final cut even if a
label were wrong.

## CLI

```bash
# read first — what's already covered, so you don't re-research it
ytclip db-coverage                                  # niches/videos + usable clips per step
ytclip db-todo <id|url> ...                         # filter candidates to those NOT yet in the store

# grow the store (concurrency-safe)
ytclip db-ingest <video_id> --niche candle_making   # add a finalized video
ytclip db-rebuild                                   # rebuild merged views + index.json
ytclip db-stats                                     # summarise the store

# select footage for assembly
ytclip shotlist --niche candle_making --per-step 3  # step-ordered list of vetted clips

# Google Drive sync (the session does the actual MCP calls; see DRIVE_SYNC.md)
ytclip drive-status                                 # Drive location + local records
ytclip drive-push-plan --have <titles…>             # which records to upload
ytclip drive-import-dir <dir>                       # import downloaded records (newest-wins) + rebuild
```

Programmatic API:

- `ytclip.shared_db`: `ingest_video`, `ingest_rows`, `import_record`,
  `usable_clips`, `flagged_windows`, `is_flagged`, `is_ingested`, `load_record`,
  `all_records`, `rebuild_views`, `stats`, `coverage`, `pending`.
- `ytclip.select`: `build_shotlist`, `write_shotlist`, `render_markdown` — picks
  the best vetted clip per canonical step (order + target durations from
  `outputs/learned_rules.yaml`), deduped for variety, and writes
  `outputs/shotlists/<niche>.{json,md}`.
- `ytclip.drive`: `config`, `local_records`, `records_to_push`, `record_text`,
  `decode`, `import_downloaded`, `import_dir` — glue around the Drive MCP calls.

## Storage / cross-chat access

The canonical store lives in **Google Drive** (folder `yt-clip-shared/`); the
local `outputs/shared_db/` is a working copy. Each session pulls new records,
ingests its own videos, and pushes the records it created. Because each video is
one uniquely-named file, concurrent contributors never collide and merges are
trivial (newest `ingested_at` wins). Full protocol + folder ids:
[`DRIVE_SYNC.md`](DRIVE_SYNC.md).

The engine itself is storage-agnostic (it operates on the `SHARED_DIR`
directory), so the same records can also be kept in git, or exported as a
read-only snapshot into claude.ai Project knowledge for Project chats to read.

## `YTA-video-maker` pipeline

All steps below are built and runnable today; the only piece left is wiring your
**skill MD** to orchestrate them (you're handling that integration).

1. **Read first** — `db-coverage` shows which niches/videos/steps are already
   covered, so you don't re-research them.
2. **Targeted research** — gather ~10 candidate videos for *this* video type
   (the broad niche is already researched) and run `db-todo <urls…>` to drop any
   already in the store.
3. **Classify in-session** — `prepare` → contact sheets → **Claude vision labels
   each 5–10s window in-session** (`ytclip prompt` prints the labeling contract)
   → `finalize` writes `outputs/<id>.timeline.json`.
4. **Ingest** — `db-ingest <id> --niche <niche>` writes the per-label shards +
   flags + index (concurrency-safe; idempotent).
5. **Select footage** — `ytclip shotlist --niche <niche>` returns a step-ordered,
   deduped, vetted (non-flagged) clip list ready for the **normal video-making
   process + rules** to assemble.

Each step is a thin CLI command / function, so the skill can call them directly
or shell out, whichever you prefer.
