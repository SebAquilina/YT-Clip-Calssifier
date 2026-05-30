# YT-Clip-Classifier

Classify **what is happening in every 5–10 second interval** of a DIY YouTube
video. The first supported domain is **candle making**: the tool segments a video
into ≤10s windows, labels each window with a candle-making action (prepare
container, melt wax, add fragrance, pour, set wick, cure, trim, reveal, …),
smooths the labels with a procedure-aware rules engine, and emits a per-video
timeline plus corpus-level *learned* rules that extrapolate to other DIY domains.

This repo ships with a **worked run over 10 real candle-making videos** (see
[`outputs/`](outputs/) and [`outputs/SUMMARY.md`](outputs/SUMMARY.md)).

---

## What it produces

For each video:
- `outputs/<id>.timeline.json` — every window `{start, end, label, confidence, evidence, notes}` + merged action `segments`
- `outputs/<id>.md` — a readable timeline table ([example](outputs/GAh9lQmaEvI.md))

For the whole corpus:
- `outputs/learned_rules.yaml` — empirically observed step order, durations, transition frequencies, coverage
- `outputs/SUMMARY.md` — human summary of the learned rules

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

10 candle videos, 436 windows classified. The **canonical step order derived from
the data** (`outputs/learned_rules.yaml`) independently recovers the real
candle-making procedure:

> prepare container → gather → measure wax → melt → add fragrance → monitor temp →
> pour → add dye → set wick → cure → decorate → trim wick → reveal

and the dominant transitions (`measure_wax → melt_wax`, `melt_wax → add_fragrance`,
`pour_wax → cure_cool`, `reveal_result → outro_cta`) match how candles are
actually made. See [`outputs/SUMMARY.md`](outputs/SUMMARY.md).

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
