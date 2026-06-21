# PIPELINE — the candle video factory, start to finish

This is the full walkthrough of how a faceless Candice candle video is made and quality-controlled,
and every check that runs. Read top to bottom. Files live in `video_dollartree_build/` (the engine)
and `skills/ai-broll-video-maker/` (this skill). Format rules referenced as v5.x / v6.

──────────────────────────────────────────────────────────────────────────
## 0. The format in one paragraph
A video alternates a small amount of **talking head** (Candice on camera, veo lip-synced) with
mostly **image-with-voiceover** beats: full-frame stills (Ken Burns), split-screen (her cropped beside
an image), come-to-life (a still animated by veo), and hands B-roll. Her cloned voice narrates the
non-TH beats. Target ~30% talking head; **never two talking-heads back-to-back**.

──────────────────────────────────────────────────────────────────────────
## 1. Author the script  (build_*.py + buildlib.py)
Helpers: `th(sentence,scene)`, `full(subject,narration)`, `split(sentence,subject,scene,side)`,
`live(subject,motion,narration)`, `br(action,narration)`, `book(sentence)` (ebook CTA).
Rules enforced at `finalize()`:
- **Short standalone lines, ≤16–18 words.** Long lines truncate at veo's 8s cap AND, if split later,
  create back-to-back THs. Write short from the start. (assert)
- **No two talking-heads in a row** (assert) — the #1 cause of "bad merge / awkward gap / speed jump".
- **MrBeast hook** (say the title at the end of the hook), **ebook CTA within 1:30**, topics in order,
  **subscribe + next-video outro**. Intro/outro/CTA are always talking head.
- `br(action, narration)` — first arg = the hand ACTION (into the veo prompt), second = the SPOKEN line.
  Never swap (a swap makes the TTS read the stage direction aloud).

## 2. Prompts that PREVENT defects  (imgkit.py)
Every prompt is assembled from reusable clauses so problems are avoided up front, not just caught:
- **IPHONE** — casual camera-roll snapshot, deep focus, natural light, faint grain, slightly imperfect
  framing; NO bokeh / studio / cinematic / 3D-CGI / stock look. (kills "too fake" images)
- **ANTIFAKE** — flame only ever a small flame ON a wick (never floating/off-a-hand/whole-object-on-fire);
  candles lit only by a match brought to the wick; real ordinary candles only (no novelty/joke/neon/
  gag-label candles); no diagrams/arrows/annotations; wax melts in a pot on a STOVE (never boiling on a
  bare table); liquids pour INTO a container (never onto the table); nothing morphs/appears.
- **NOSPAWN** — for B-roll/come-to-life: every object present from frame 1, nothing pops in/out.
- **NOMUSIC** — talking-head audio is her voice + room tone only, no soundtrack.
- **NOTEXT** — zero burned-in captions/subtitles/watermark/UI; only real product labels allowed.
- **IDENTITY** — locks Candice's exact face/hair/glasses/sweater/apron.
Never write "shallow depth of field", "diagram", or "cross-section" in a prompt.

## 3. Reference images  (refs_build.py)
Veo uses the keyframe as the clip's FIRST frame, so soft anchors = soft talking heads. Generate sharp,
identity-locked scene keyframes (bench/kitchen/shelf/packing/window) + one canonical empty-workbench
reference, pick the best of each, host them; `/tmp/scene_refs.json` + `/tmp/bench_ref.txt` override the
defaults. The bench ref is passed as the img2img reference on every image beat for a consistent bench.

## 4. Generate  (gen_dt_par.py)
One process, semaphore-capped at the real API limits: **5 concurrent veo videos, 7 images, 2 TTS**.
Beats are independent so they run concurrently; a single state.json is written under a lock (no race).
Resumable — re-running fills only missing assets. For very long videos, generation order does not affect
the final cut (the assembler reads beats in manifest order), so concurrency is purely speed.

## 5. THE GATE SUITE — run ALL of these before every assembly, and AGAIN after any re-roll
1. **Imposter face scan** (`face_scan.py`, 2-class ArcFace: Candice centroid vs imposter centroid) —
   0 wrong-face clips allowed. `face_check_ids.py` is the fast targeted version for re-rolls.
2. **No-text / watermark vision scan** — 3 frames/clip + stills inspected by vision agents for burned-in
   captions / Veo watermark / UI / arrow-diagrams. (tesseract is unreliable on veo's low-contrast text.)
3. **Realism vision scan** — 3 frames/clip; flags spawning/vanishing objects, flames off a wick, candles
   lit from afar, fake/CGI/novelty candles, wax boiling on a table, pouring onto a table, resin-on-fire.
4. **Coherence gate** (`deep_gate.py`) — full-transcript similarity (catches gibberish + veo junk words
   like "tat" + duplicate adjacent lines), via small.en whisper.
5. **Truncation / muted gate** — small.en + tail-presence: every veo-spoken line says its whole sentence;
   no muted clips; narration TTS isn't cut off.
6. **Adjacency + rate** (`deep_gate.py`) — runs of ≥2 talking-heads, mid-clause fragments, and speech-rate
   outliers reported.
**THE RULE THAT WAS MISSING:** any clip re-rolled to fix a flaw must be re-scanned (face especially) —
re-rolls after the scan are how imposters/text slipped through. The orchestrator + per-fix face checks
now enforce this.

## 6. Auto-fix loop  (finish_video.py)
Runs face + truncation + coherence, pops flagged beats' clip (or audio), regenerates, re-checks — with a
per-beat retry cap so it can't loop forever — then assembles + masters. Realism is a vision pass run
separately (agents), with the same re-roll-then-rescan discipline.

## 7. Assemble  (asm_dt.py)
Per beat → one 1280×720/24fps segment, then a chunked crossfade join (the 100+-input single graph is too
big for one ffmpeg call). Built-in fixes:
- **delogo** the veo watermark bottom-right.
- **Per-segment volume gain** to a common loudness (sample-aligned — NOT dynamic loudnorm, which delayed
  audio and desynced lips).
- **Narration rate-match**: pitch-preserving atempo slows the cloned TTS (~3.1 wps) to a consistent
  ~2.1 wps, close to veo TH (~1.8) — fixes the cross-track speed mismatch (TH is never stretched).
- **Trailing-silence crop** on TH/split so clips don't sit in dead air.
- **Face-centered split crop** — detects Candice's face and crops the TH pane around it (no half-cut).
- **1:1 split images, cover-fit** (never squeezed/warped).
- **Book CTA** — composites the REAL book cover as an inset (veo renders books poorly).
- Per-boundary crossfade: 0.12s between consecutive face beats, 0.25s at scene changes.

## 8. Master + deliver  (master_audio.py)
High-pass + light denoise + two-pass EBU R128 loudnorm to **-16 LUFS / -1.5 dBTP** + faint room-tone bed.
Deliver as a zip: final video + all source clips + thumbnail + description (book CTA link → chapters →
hashtags). Thumbnail = nano-banana background (Candice + props, identity-locked) + bold title text via PIL.

──────────────────────────────────────────────────────────────────────────
## 9. Defect → which gate catches it (quick map)
| Defect | Caught by |
|---|---|
| Wrong face / imposter | face_scan (#1) |
| Burned-in caption / watermark | no-text vision (#2) |
| Flame off wick, spawn, fake/novelty candle, wax on table, resin on fire | realism vision (#3) + ANTIFAKE prompt |
| Gibberish / "tat" / duplicate line | coherence deep_gate (#4) |
| Sentence cut off / muted clip | truncation gate (#5) |
| Two THs in a row / mid-clause fragment | adjacency (buildlib assert + #6) |
| TTS faster than TH / speed drift | rate-match atempo (assembler) |
| Background music | NOMUSIC prompt |
| Soft talking head | sharp scene keyframes (refs_build) |
| Warped split image | 1:1 + cover-fit (assembler) |
| Lip-sync drift | volume-gain leveling, not dynamic loudnorm (assembler) |

Golden rule: **run the whole of §5 before delivery, and re-run it after every re-roll.**
