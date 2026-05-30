# Deep research: prior art

Goal: classify what happens in every 5–10s interval of a video and learn rules
that extrapolate. Survey of existing work and how each piece informed this repo.

## Directly comparable projects

### `op7418/Youtube-clipper-skill` (the reference)
A Claude **skill** that downloads a video + English subtitles with `yt-dlp`, has
Claude read the **subtitle text** to find semantic chapters (2–5 min), then cuts
clips with `FFmpeg` and burns bilingual subtitles.
- **Borrowed:** the `yt-dlp` → `ffmpeg` download/clip plumbing and the
  "let Claude do the semantic call" idea.
- **Why it isn't enough here:** it segments on *transcript text* at *2–5 min*
  granularity. Candle-DIY videos are mostly **visual** (often music-only) and we
  need **5–10s** granularity, so the signal and the resolution are both wrong.
  We replace the transcript-driven chaptering with a **visual** window classifier.

### Vision-LLM "watch a video" tools
- [`bradautomates/claude-video`](https://github.com/bradautomates/claude-video) —
  downloads, extracts frames at an auto-scaled rate, pulls a timestamped
  transcript, hands frames to Claude as images.
- [`jordanrendric/claude-video-vision`](https://github.com/jordanrendric/claude-video-vision) —
  ffmpeg frame extraction + audio backends, Claude receives frames + timestamps.
- Google [Gemini video understanding](https://ai.google.dev/gemini-api/docs/video-understanding)
  can natively reference `MM:SS` timestamps and segment a video.
- **Borrowed:** the **frames → vision model → timestamped labels** pattern. Our
  contact-sheet montage is a token-efficient variant (many windows per image).

## Shot / scene segmentation (window boundaries)
- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) — OpenCV
  content-based shot-cut detection. **Used** in stream mode to place window
  boundaries on real cuts before enforcing the 5–10s bounds.
- [`albanie/shot-detection-benchmarks`](https://github.com/albanie/shot-detection-benchmarks)
  and the FFmpeg `select='gt(scene,...)'` filter — alternatives/benchmarks.
- [AnyiRao/SceneSeg](https://github.com/AnyiRao/SceneSeg) (CVPR'20) — multi-modal
  movie scene segmentation; informs the "features → temporal grouping" split.

## Instructional-video step segmentation (the real analogue)
DIY candle making is structurally a **procedure with ordered steps**, exactly the
setting these datasets/papers study:
- [COIN](https://github.com/coin-dataset/code) — 11k instructional videos labelled
  with step boundaries; benchmark for **step localization**.
- [YouCook2 / ProcNets](https://github.com/LuoweiZhou/ProcNets-YouCook2) — cooking
  videos with temporally-localized, ordered procedure steps.
- [awesome-temporal-action-segmentation](https://github.com/nus-cvml/awesome-temporal-action-segmentation)
  — survey of per-frame action segmentation methods.
- Open-vocabulary **zero-shot** action segmentation with VLMs (frame–action
  embedding similarity + temporal smoothing) — the training-free recipe we mirror:
  vision model proposes per-window labels, a temporal rules pass enforces order.

**Borrowed:** the procedure-step framing (ordered steps + a canonical order prior)
and the idea of a temporal-consistency post-process — implemented here as
`config/rules.yaml` + `src/ytclip/rules.py`, with the order **learned back** from
the corpus in `ytclip learn`.

## Synthesis → what this repo adds
1. A **candle-DIY action taxonomy** with per-label visual cues, phase grouping,
   and order/duration priors (`config/taxonomy.yaml`).
2. A **storyboard fallback** so classification works even where video download is
   blocked — using YouTube's own thumbnail sheets as a dense frame source.
3. **Contact-sheet montages** so a vision model labels many 5–10s windows per
   image instead of one frame per call.
4. A **rules engine** that smooths labels and checks them against a canonical
   procedure order, plus a **learning step** that re-derives that order, step
   durations and transition statistics from the labelled corpus — the mechanism
   by which the rules "extrapolate" to new videos and new DIY domains.
