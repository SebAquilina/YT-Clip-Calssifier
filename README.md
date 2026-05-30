# YT-Clip-Classifier

Classify **what is happening in every 5–10 second interval** of a DIY YouTube
video. The first supported domain is **candle making**: the tool segments a video
into ≤10s windows, labels each window with a candle-making action (prepare
container, melt wax, add fragrance, pour, set wick, cure, trim, reveal, …),
smooths the labels with a procedure-aware rules engine, and emits a per-video
timeline plus corpus-level *learned* rules that extrapolate to other DIY domains.

This repo ships with a **classified database of 100 real candle-making videos**
(**4,315** labelled 5–10s windows) — see [`outputs/db/`](outputs/db/) and
[`outputs/SUMMARY.md`](outputs/SUMMARY.md).

---

## What it produces

For each video:
- `outputs/<id>.timeline.json` — every window `{start, end, label, confidence, evidence, notes}` + merged action `segments`
- `outputs/<id>.md` — a readable timeline table ([example](outputs/GAh9lQmaEvI.md))

For the whole corpus:
- **`outputs/db/classifications.{sqlite,csv,jsonl}`** — the full database: **one row per 5–10s window**, each with the video link, a timestamped deep-link (`youtu.be/<id>?t=<start>s`), action label, phase, confidence, a **detailed description**, the **objective features** (`face_score`, `text_score`, `ocr_text`, `motion`, `brightness`, `colorfulness`, `dominant_colors`), and the filter result (`keep`, `filter_reason`, `validation_flags`).
- **`outputs/db/classifications_clean.{csv,jsonl}`** — the **action-only subset**: talking-head and text/title/card windows removed (also the `windows_clean` view in SQLite). This is the "no talking-head, no text-overlay" corpus.
- `outputs/learned_rules.yaml` / `outputs/SUMMARY.md` — empirically observed step order, durations, transitions.

**Anti-hallucination:** every window's description is paired with code-computed signals (face/OCR/motion/…) that corroborate or contradict it, and a validator records `validation_flags` for genuine label↔evidence conflicts. See `docs/METHODOLOGY.md` §6–7. Refresh signals with `python -m ytclip.cli analyze` and rebuild with `build-db`.

Build/refresh the database any time with `python -m ytclip.cli build-db`.

### The 100-video database

`outputs/db/` holds **100 candle videos / 4,315 windows**. Querying it (e.g.
`sqlite3 outputs/db/classifications.sqlite "select action_label,count(*) from windows group by 1 order by 2 desc"`)
and the `ytclip learn` aggregation independently recover the real candle-making
procedure from the data:

> gather materials → prepare container → measure wax → melt wax → add fragrance →
> add dye → monitor temp → pour wax → decorate → set wick → cure → reveal → trim wick

> The 5–10s cap is enforced on **windows**. Consecutive windows with the same
> label are then merged into action **segments** for readability, so a segment
> (e.g. a 32s `melt_wax`) can be longer — it is just several ≤10s windows of the
> same action.

---

## How it works

```
                 ┌─────────────┐   bot-gated?  ┌──────────────────┐
 YouTube  ─────► │  download   │ ───stream───► │  PySceneDetect   │ shot cuts
                 │  (yt-dlp)   │               │  + cv2 frames    │
                 └──────┬──────┘               └──────────────────┘
                        │ fallback (works on cloud IPs)
                        ▼
                 ┌─────────────┐   thumbnails   ┌──────────────────┐
                 │ storyboards │ ─────────────► │ 5–10s windowing  │
                 └─────────────┘                └────────┬─────────┘
                                                         ▼
        ┌────────────────┐   labelled grid   ┌──────────────────────┐
        │ contact-sheet  │ ────────────────► │ vision classifier    │
        │   montage      │                   │ (Claude vision) →     │
        └────────────────┘                   │  one label / window   │
                                             └──────────┬───────────┘
                                                        ▼
                                          ┌──────────────────────────┐
                                          │ rules engine: despike,    │
                                          │ gap-fill, canonical-order │
                                          │ checks → timeline + md     │
                                          └──────────────────────────┘
```

Two frame sources, one downstream pipeline:

1. **Stream mode** (best quality) — `yt-dlp` downloads a ≤480p stream,
   `PySceneDetect` finds shot cuts, windows snap to cuts (split >10s, merge <5s),
   `OpenCV` extracts representative frames.
2. **Storyboard mode** (always available) — when streams are unavailable
   (e.g. a bot-gated cloud IP, see [Notes](#notes-on-the-environment)), the tool
   pulls YouTube **storyboard** thumbnails (~1 frame / 1.8s) and builds uniform
   5–10s windows. Lower resolution, but enough for coarse action labels — the
   10 bundled runs all use this mode.

Each window's frames are tiled into a captioned **contact sheet**; a vision model
(Claude) reads the sheet and returns one label per window. The **rules engine**
(`config/rules.yaml`) then cleans the raw labels and flags implausible reversals
of the canonical candle-making order.

---

## Taxonomy

The classification scheme lives in [`config/taxonomy.yaml`](config/taxonomy.yaml).
Labels are grouped into domain-independent **phases** so the schema generalises:

| phase | candle-DIY labels |
|-------|-------------------|
| intro | `intro_titlecard` |
| prep | `gather_materials`, `prepare_container`, `measure_wax` |
| process | `melt_wax`, `monitor_temperature`, `add_fragrance`, `add_dye_color` |
| assemble | `pour_wax`, `set_wick`, `cure_cool` |
| finish | `trim_wick`, `decorate_finish`, `reveal_result` |
| aux | `outro_cta`, `talking_head`, `transition`, `other_unclear` |

To support a new domain (soap, resin, baking) you only swap the `process` phase —
see `generalization:` in `config/rules.yaml`.

---

## Install & run

```bash
pip install -r requirements.txt        # yt-dlp, scenedetect, opencv, pillow, requests, pyyaml
export PYTHONPATH=src

# 1. find candidate videos
python -m ytclip.cli search "candle making diy tutorial" -n 10

# 2. fetch frames -> windows -> contact sheets -> a labels stub
python -m ytclip.cli prepare <video_id>            # add --no-stream to force storyboards

# 3. classify: open data/work/<id>/sheets/*.jpg, fill outputs/<id>.labels.json
#    (each tile is one window: {"window": i, "label": "...", "confidence": .., "evidence": ".."})
python -m ytclip.cli prompt                        # prints the exact classification prompt + label reference

# 4. apply the rules engine -> timeline + markdown
python -m ytclip.cli finalize <video_id>

# 5. aggregate every finalized video -> learned rules
python -m ytclip.cli learn
```

### The classification step

There is no standalone model call baked in: the vision step is done by **Claude**
(via the contact sheets), because that is both the most accurate option for niche
candle actions and the way these runs were produced. `ytclip prompt` prints the
ready-to-use instruction block. To wire in an automated API call, drop a function
that reads `data/work/<id>/sheets/*.jpg` and writes `outputs/<id>.labels.json` —
the rest of the pipeline is unchanged.

---

## Results in this repo

**100 candle videos, 4,315 windows classified** — a broad spread of soy/beeswax/
coconut/paraffin builds, layered & ombre candles, dipped tapers, rolled & carved
& flower & dessert candles, plus kit/business/care videos. Every window carries a
detailed description and a timestamped link in `outputs/db/`. The **canonical step
order derived from the data** (`outputs/learned_rules.yaml`) independently recovers
the real candle-making procedure, and the dominant transitions (`measure_wax →
melt_wax`, `melt_wax → add_fragrance`, `pour_wax → cure_cool`) match how candles
are actually made. See [`outputs/SUMMARY.md`](outputs/SUMMARY.md).

---

## Notes on the environment

These runs were produced in a sandbox whose egress IP is **bot-gated by YouTube**
(every muxed stream returns *"Sign in to confirm you're not a bot"* or DRM), so
the pipeline used **storyboard mode**. On a normal machine (residential IP and/or
browser cookies) `prepare` will download real streams and use the higher-quality
PySceneDetect + OpenCV path automatically.

The sandbox also routes egress through a TLS-inspecting proxy whose CA is in the
system trust store but not in `certifi`; the downloader passes
`--compat-options no-certifi` so yt-dlp uses the system trust store (it trusts an
already-trusted CA — it does **not** disable verification).

See [`docs/RESEARCH.md`](docs/RESEARCH.md) for prior art and
[`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for the design rationale.
