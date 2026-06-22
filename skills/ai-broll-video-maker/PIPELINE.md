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
## 1. Author the script  (build_*.py + buildlib.py)  — honors the xlsx blueprint AND the Yoder playbook
The script must satisfy BOTH the per-video **content blueprint** (the ideation xlsx "Script Blueprint":
hook, ebook topic, MUST-COVER topics in order, length, outro — parse with `blueprint_parse.py`) AND the
**Elias-Yoder retention playbook** (`references/retention-playbook.md`). Tag retention beats with `role=`
(cold_open / withheld / dark_loop / villain / honesty / escalation / story / stakes / recap / comment_bait
/ sequel_hook / signoff …), `coin()` one phrase and repeat it, and end on `SIGNOFF`. Then
**`script_lint.py <project> --xlsx <xlsx> --title "<t>"` is a HARD GATE** (run after finalize, before
generation) that fails unless every MUST-COVER topic AND every required retention element is present.
Helpers: `th(sentence,scene,role=)`, `full(subject,narration,role=)`, `split(...,role=)`,
`live(...,role=)`, `br(...,role=)`, `cta_ebook(line_ebook,line_trust,scene1,scene2)`, `coin(phrase)`.
Rules enforced at `finalize()`:
- **Short standalone lines, ≤16–18 words.** Long lines truncate at veo's 8s cap AND, if split later,
  create back-to-back THs. Write short from the start. (assert)
- **No two talking-heads in a row** (assert) — the #1 cause of "bad merge / awkward gap / speed jump".
- **MrBeast hook** (say the title at the end of the hook), topics in order, **subscribe + next-video outro**.
  Intro/outro/CTA are always talking head.
- **EBOOK CTA (v6.4 SOP, within 1:30):** `cta_ebook(...)` emits TWO talking-head beats in DIFFERENT scenes
  — beat 1 composites the real ebook cover and ties THIS video's topic to it; beat 2 (new scene) is the
  TRUST line ("it's there if you want it, I won't mention it again" + "I'm tired of people wasting money on
  candles a few small cheap changes would fix"). Always say **ebook**, never "book"; mention it ONCE.
- **Subject continuity — TWO AGENTS (v6.5):** `finalize()` writes a `auto_subject_refs()` heuristic
  baseline, then run `subject_agents.py <project>` — a team of two agents (driven by the Claude Code build
  subagents, or the Anthropic API): **Agent 1 (Subject Director)** segments every still into evolving
  subjects + stages and flags counter-examples; **Agent 2 (Continuity Supervisor)** picks each beat's
  img2img reference = the predecessor STAGE of the same subject. It writes `subject_plan.json` and stamps
  `subject_ref_of` (replacing the heuristic) so a DIY subject evolves consistently and bad-example shots
  never inherit the hero. `gen_dt_par` renders roots first and defers a beat until its reference exists.
  `subj=` still hard-overrides. See SKILL.md FORMAT v6.5.
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
**Model routing (v7):** talking heads (full + split TH pane, `engine:"grok"`) → **grok-imagine-video**
(10s/720p, image-to-video off the scene keyframe, fixed voice in the prompt); come-to-life stills + hands
b-roll → **veo-lite**; stills → nano-banana-pro. See `references/grok-video-th.md`.
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
5. **Truncation / muted gate** — small.en transcription, checked at BOTH ends:
   - **tail-presence**: every veo-spoken line says its whole sentence (no end cut-off);
   - **lead-in gibberish (v6.2)**: the transcript must START on the script's opening words — veo sometimes
     prepends hallucinated words (e.g. *"Once I'm through making Comfrey and Paracyme, okay, I did…"*).
     If unrelated words precede the line, re-roll. The hook especially must open clean.
   - **muted-stream (v6.2)**: `ffprobe` must show an audio track on every TH (a re-roll came back silent).
     A muted TH is a hard fail; muted broll/live is fine (narration is added at assembly).
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
- **Narration at NATURAL speed** (`NARR_ATEMPO=1.0`): the 69labs cloned TTS already comes out at the
  right cadence — play it UNCHANGED. (We used to slow it to ~0.66×; it sounded draggy and was the #1
  complaint. Never stretch narration OR talking head.) Segment length follows the narration's own
  duration, so the cut self-adjusts and runs ~15-20% shorter.
- **Trailing-silence crop** on TH/split so clips don't sit in dead air.
- **Face-centered split crop** — detects Candice's face and crops the TH pane around it (no half-cut).
- **1:1 split images, cover-fit** (never squeezed/warped).
- **Book CTA** — composites the REAL book cover as an inset (veo renders books poorly).
- Per-boundary crossfade: 0.12s between consecutive face beats, 0.25s at scene changes.

## 8. Master + deliver  (master_audio.py)
High-pass + light denoise + two-pass EBU R128 loudnorm to **-16 LUFS / -1.5 dBTP** + faint room-tone bed.
Deliver as a zip (`build_deliverable.py`): final mastered video + all source clips + `thumbnails/` (all 6:
3 concepts × 2 variants, nano-banana-pro @ 2k) + `description.txt` + `tags.txt`.
- **Description** (v6.4): first line is short, video-specific, says **ebook**, and prefixes the link with 🔗.
  Order: ebook teaser+link → body → chapters → closing → hashtags. CTA chapter reads "My ebook (free first
  chapter)".
- **Tags** (v6.4): `gen_tags.py <proj> "specific,tags"` writes `tags.txt` (CSV) — video-specific tags +
  broad evergreen/cross-platform pool (diy, candlemaking, tiktok, reels…), de-duped, ≤500 chars.
- **Chapters are computed from the FINAL cut, never hand-set** (v6.2): runtimes change (especially after
  the natural-speed fix), so run `chapters_gen.py <proj> <build_script> "<hook title>"` — it parses the
  build script's `# ===== SECTION =====` headers, times each section's first beat against the real
  assembled segments (replaying the chunked-crossfade math), merges sub-sections <11s apart, and prints
  `M:SS  Title`. Swap that into the `⏱️ Chapters` block. Verify the book CTA chapter lands < 1:30.
- **NEVER commit rendered media** — `.mp4/.mp3/.png/.zip` are git-ignored and hosted (litterbox). A stray
  1.5 GB of committed videos makes `git push` fail with HTTP 413; keep the repo to source + small files.

──────────────────────────────────────────────────────────────────────────
## 9. Defect → which gate catches it (quick map)
| Defect | Caught by |
|---|---|
| Wrong face / imposter | face_scan (#1) |
| Burned-in caption / watermark | no-text vision (#2) |
| Flame off wick, spawn, fake/novelty candle, wax on table, resin on fire | realism vision (#3) + ANTIFAKE prompt |
| Gibberish / "tat" / duplicate line | coherence deep_gate (#4) |
| Sentence cut off at the END | truncation gate (#5) |
| Lead-in gibberish before the line (start) | trunc_check lead-in check (#5, v6.2) |
| Muted talking head (no audio stream) | trunc_check ffprobe audio check (#5, v6.2) |
| Two THs in a row / mid-clause fragment | adjacency (buildlib assert + #6) |
| Narration too slow / draggy / "not real" | `NARR_ATEMPO=1.0` — never stretch TTS (assembler, v6.2) |
| Wrong chapter timestamps after a re-cut | recompute with `chapters_gen.py` (v6.2) |
| Background music | NOMUSIC prompt |
| Soft talking head | sharp scene keyframes (refs_build) |
| Warped split image | 1:1 + cover-fit (assembler) |
| Lip-sync drift | volume-gain leveling, not dynamic loudnorm (assembler) |
| Push fails (HTTP 413) | never commit rendered media — git-ignore .mp4/.mp3/.png/.zip (v6.2) |

Golden rule: **run the whole of §5 before delivery, and re-run it after every re-roll.**
