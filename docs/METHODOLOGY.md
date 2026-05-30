# Methodology

## 1. The classification decision

The task ("decide how to classify the movements / what is being shown") is framed
as **procedure-step labelling**: each 5–10s window is assigned exactly one action
from a fixed taxonomy. This is preferred over free-form captioning because:

- it is **evaluable** (fixed label set → coverage, transition stats, agreement),
- it supports a **rules engine** (a canonical order only exists over discrete steps),
- it **generalises** — steps are grouped into domain-independent *phases*.

### Taxonomy design (`config/taxonomy.yaml`)
Each label carries: a `phase`, a human `description`, concrete `visual_cues` (fed
to the vision model), a `typical_position` (0–1) and `typical_duration`, and an
`is_step` flag separating real procedure steps from auxiliary content
(intro/outro/talking-head/transition). Candle steps:

`gather_materials → prepare_container → measure_wax → melt_wax →
monitor_temperature → add_fragrance / add_dye_color → pour_wax → set_wick →
cure_cool → trim_wick → decorate_finish → reveal_result`

## 2. Windowing (≤10s, snap to action)

`config/rules.yaml::windowing` sets `min=5, max=10, target=8`.
- **Stream mode:** PySceneDetect yields shot spans; spans >10s are split into
  ~8s sub-windows, spans <5s are merged forward (without crossing 10s). Boundaries
  thus align to real cuts where possible.
- **Storyboard mode:** the duration is tiled into ~8s windows; storyboard
  thumbnails (≈1 / 1.8s) are assigned to the window they fall in, and up to 3
  spread frames (first / middle / last) represent each window.

The hard 10s cap is always enforced on windows. (Merged *segments* in the reports
may be longer — they are runs of same-labelled windows.)

## 3. Vision classification

Per-window frames are tiled into a captioned **contact sheet**
(`src/ytclip/montage.py`); each tile shows a window's frame-strip with
`W{index} {start}-{end}s`. A vision model (Claude) reads the sheet and returns
`{window, label, confidence, evidence}` per tile. Packing many windows into one
image keeps the number of model calls ~`ceil(windows/24)` instead of one per
window. The exact prompt + label reference is emitted by `ytclip prompt`.

On-screen step captions ("Melt wax using double boiler", "Pour at 135°F",
"Cut the Wick") are treated as strong evidence when present.

## 4. Rules engine (`src/ytclip/rules.py`)

Raw labels are noisy (low-res storyboards, ambiguous frames), so a temporal pass
cleans them:
- **despike** — an isolated window whose two identical neighbours disagree with it
  (and confidence <0.8) is rewritten to the neighbour label.
- **gap-fill** — a low-confidence window (<0.55) bracketed by an agreeing pair is
  filled.
- **backward-jump check** — labels are scored against `canonical_order`; a step
  that regresses (and is not a known `repeatable` pair such as
  `melt_wax↔monitor_temperature` or `pour_wax↔set_wick`) is annotated.
- Auxiliary labels are exempt from order penalties.

Every override is recorded (`smoothed`, `notes`) so the report is auditable.

## 5. Learning rules that extrapolate (`src/ytclip/learn.py`)

`ytclip learn` aggregates all finalized timelines into `learned_rules.yaml`:
- `observed_position` — mean normalized position of each label,
- `derived_canonical_order` — steps sorted by that position,
- `observed_duration_s` — mean/median per step,
- `top_transitions` — most frequent label→label moves,
- `coverage_videos` — how universal each step is.

This closes the loop: the hand-written priors bootstrap classification, and the
corpus **re-derives** the order, durations and transitions from data. In the
bundled 10-video run the derived order reproduces the real candle procedure and
the top transitions are the genuine production flow (`measure_wax→melt_wax`,
`melt_wax→add_fragrance`, `pour_wax→cure_cool`, `reveal_result→outro_cta`),
validating the taxonomy. These learned statistics are the artifact you carry to
**new videos** (better priors) and, by swapping the `process` phase, to **new DIY
domains**.

## 6. Objective features & anti-hallucination (`src/ytclip/features.py`)

Because the model's descriptions are an interpretation of low-res frames, every
window also gets **code-computed, reproducible measurements** that can corroborate
or contradict the label — these are stored on every row so nothing is taken on
trust:

| feature | how | what it grounds |
|---|---|---|
| `face_score` | OpenCV Haar frontal-face cascade (frames upscaled 4×) | talking-head |
| `text_score` | OpenCV MSER text-region coverage | on-screen text |
| `ocr_text` / `ocr_charcount` | Tesseract on the middle frame (gated on text presence) | **verbatim captions** (so caption claims come from OCR, not the model) |
| `motion` | mean abs frame-diff across the window | static card vs live action |
| `brightness`, `colorfulness`, `dominant_colors` | luma / Hasler–Süsstrunk / k-means | blank frames, scene character |

**Validation (`filtering.validate_window`)** cross-checks the model's
label/description against these features and emits `validation_flags`, e.g.
*"action label 'pour_wax' but a strong face fills the frame"*, *"active label on a
near-black frame"*, or *"description references on-screen text but OCR found none"*.
Flagged rows are surfaced in the DB for review. The description protocol
(`ytclip prompt`) also requires separating observation from inference and only
quoting captions that are actually legible.

We validated the face detector against the hand labels: on a talking-head-heavy
video it agreed with the manual `talking_head` windows **87%** of the time, and
OCR recovered real burned-in captions (e.g. "Add 0.5 oz fragrance") off the
hands-on frames.

## 7. Filtering talking-head & text-overlay windows (`src/ytclip/filtering.py`)

Driven by the objective features (thresholds in `config/filter.yaml`), each window
is tagged `keep` + `filter_reason`:
- **`talking_head`** — `face_score ≥ 0.40`.
- **`text_overlay`** — a *static* text card: substantial OCR text **and**
  `motion < 0.02` **and** no face. The motion gate is the key discriminator that
  **keeps captioned action** (which always moves) while removing title/end/promo
  slides — exactly the requested policy.
- **`blank`** — near-black or flat/empty frames.

Filtering is non-destructive: the full DB keeps every window with its flag, and a
separate **clean action-only subset** (`classifications_clean.*`, also the
`windows_clean` SQLite view) = `keep AND is_step`. On new videos
`pipeline.autolabel_stub` pre-labels the filtered windows from the detectors, so
the model only writes detailed descriptions for the hands-on windows.

## 8. Limitations & next steps

- **Storyboard resolution (160×90)** makes fine actions (fragrance vs dye, wick
  centering) ambiguous → moderate confidences. Stream mode removes this.
- **No audio/transcript** signal yet; adding ASR would disambiguate talking-head
  vs hands-on and catch spoken step cues.
- **Single-label per window**; brief overlapping actions get the dominant label.
- The vision step is currently agent-in-the-loop; wiring a direct API call (read
  sheets → write `labels.json`) would make end-to-end runs unattended.
