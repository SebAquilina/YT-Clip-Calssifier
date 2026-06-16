---
name: ai-broll-video-maker
description: >-
  Drop-in B-roll engine swap for the ultimate-video-maker factory: same sheet-row
  → published video, but EVERY body shot is AI-generated on 69labs (Veo 3.1 Lite)
  in the Elias-Yoder documentary style — footage that looks shot on an iPhone,
  always literally matched to the exact sentence being narrated, so it feels like
  a real person filmed it. Script, persona/character, thumbnail, hook, talking-head
  inserts, voiceover, revoice, assembly and publishing are INHERITED UNCHANGED from
  ultimate-video-maker; this skill replaces ONLY the corpus/YouTube B-roll source
  with bespoke per-sentence AI clips generated in waves of up to 5 concurrent jobs,
  and keeps the talking-head-interrupts-B-roll rhythm. Use whenever the B-roll
  should be AI-generated rather than corpus-matched, or the user mentions the
  "Elias Yoder style", "iPhone-shot B-roll", AI B-roll for a whole video, "make
  video N with generated footage", or a faceless Amish / old-ways / lost-knowledge
  channel. Prefer over ultimate-video-maker when B-roll must be AI.
---

# AI B-roll Video Maker — every shot generated, iPhone-real, sentence-matched

This is the **ultimate-video-maker factory with one component swapped**: the
B-roll no longer comes from the scraped corpus (clip-corpus-builder +
video-maker-3's matcher + picker agents). Instead, **every body shot is an AI
clip generated on 69labs, in the Elias-Yoder documentary look** — handheld,
iPhone-grade, period-accurate, and tied literally to the sentence on the
voiceover at that instant. Nothing else about the factory changes.

**Read `ultimate-video-maker`'s SKILL.md first** — it is the parent. You run its
pipeline verbatim for everything except B-roll. This skill only rewrites its
Stage 5 + Stage 6 (the corpus B-roll engine) and adjusts Stage 9's gates.

Read before the first run of a session:
- `references/iphone-broll-doctrine.md` — the Elias-Yoder B-roll aesthetic: the
  iPhone token block, shot tiers, the "a real person made this" principle, and
  worked B-prompt examples. **This is the heart of the skill.**
- `references/beat-segmentation-and-continuity.md` — how to cut each body
  segment's narration into 6–9 s visual beats, one clip per beat, and how to
  keep the world continuous across dozens of separately-generated clips.
- `references/period-authenticity-panel.md` — the niche reality gate that keeps
  anachronisms and AI tells out of every shot.
- `references/veo-prompting.md` — Google's Veo 3.1 prompting rules (inherited
  verbatim; obey them on every prompt).
- `references/69labs-video-workflow.md` — field-tested 69labs mechanics
  (keyframe attach, capture via `directFileUrl`, quota, outage handling).

## The one-line doctrine

> **The viewer must believe a real person walked through a real place with a
> phone and filmed exactly the thing the narrator is describing, right now.**

Everything below serves that sentence. Polished, cinematic, shallow-depth-of-
field footage BREAKS it — in this niche, slightly-rough phone footage reads as
authentic and trustworthy, and that authenticity is the whole product. Footage
that is thematically near the sentence but not literally OF it reads as stock
B-roll and breaks it too. Literal + iPhone-real = the channel.

## Inherited UNCHANGED from ultimate-video-maker (do not re-implement)

Run the parent skill exactly as written for all of these — the persona, the
script, and the character are explicitly out of scope for this skill:

- **Stage 0** gather + `ultimate_manifest.json` + task list.
- **Stage 1** sheet lookup + measured-WPM pace calibration.
- **Stage 2** thumbnail (thumbnail-factory, Thumbnail A).
- **Stage 3** hook clip (thumbnail-to-vid, reality-panel gated, revoiced).
- **Stage 4** script: Retention Opening → MrBeast breakdown → Retention Outro,
  written in the channel persona, as the **SEGMENTED voiceover** (the CTA + N
  talking heads ⇒ N+2 body segments). **This segmented structure is exactly
  what produces the "B-roll interrupted by the talking head" rhythm Elias Yoder
  uses — keep it.** See the parent's `references/segmented-voiceover.md`.
- **Stage 7** character clips (CTA + each talking head, Mode A, reference photo
  keyframe), each revoiced with `/ultimate-revoice` per the parent's REVOICE
  RULE.
- **Stage 8 assembly** = pure normalize + CONCATENATION in the fixed order
  `hook → body₀ → CTA → body₁ → TH1 → body₂ → … → body_N → TH_N → body_{N+1}`
  via the parent's `scripts/assemble_segmented.py`. Nothing is cut.
- **Stage 9.5** finalize/saving SOP.

The talking heads are **A-mode character clips** and are generated and revoiced
by the parent's Stage 7 — this skill does not touch them. What this skill owns
is **every body segment's visuals**.

## REPLACED by this skill: the body B-roll engine (parent Stages 5–6)

The parent matched each body segment to corpus windows with picker agents and
sprinkled a few AI gap-fillers. **Delete that whole path.** In its place, each
body segment is filled, start to finish, by AI clips generated for its exact
sentences. The new sub-pipeline, per body segment:

```
narrate segment (69labs TTS, channel voice)            [parent Stage 5 narration — KEEP]
   ↓
force-align → cut into 6–9 s VISUAL BEATS               [scripts/segment_beats.py]
   ↓
write one iPhone B-mode Veo prompt PER BEAT             [iphone-broll-doctrine.md]
   ↓  (sentence quoted at top; continuity bible injected)
period-authenticity panel on every prompt              [period-authenticity-panel.md]
   ↓
generate in WAVES OF 5 on 69labs (Veo 3.1 Lite)        [scripts/batch_generate.py]
   ↓
capture (directFileUrl) → trim/pad each clip to its beat [scripts/trim_and_place.py]
   ↓
concat the beat clips into body_<n>.mp4 over its narration
```

Then the parent's Stage 8 concatenates `body_<n>.mp4` with the hook, CTA, and
talking heads exactly as before. **There is no corpus, no matcher, no picker
agent, and no corpus registration** in this skill — every body clip is bespoke
to this one video.

---

## Stage B1 — beat segmentation (one clip per sentence-beat)

Full method: `references/beat-segmentation-and-continuity.md`. Summary:

1. Generate each body segment's narration as a 69labs TTS MP3 in the channel
   voice (same as the parent's Stage 5 — `LABS69_API_KEY`, `LABS69_VOICE_ID`,
   `LABS69_VOICE_PROVIDER=elevenlabs`). One MP3 per body segment.
2. `python3 scripts/segment_beats.py --audio body_<n>.mp3 --script body_<n>.md
   --out beats_<n>.json` force-aligns the narration (faster-whisper) and cuts it
   into **6–9 s beats at sentence / strong-clause boundaries** (never mid-phrase).
   Each beat records: `id`, `start`, `end`, `dur`, and the **verbatim sentence**
   it covers.
3. **One beat = one shot = one thing on screen.** A beat is the smallest unit
   that has a single concrete visual. If a sentence packs two visuals ("the
   cupola on the roof, the muslin under the rafters"), split it into two beats so
   each gets its own clip. If a sentence is abstract with no image, it becomes a
   **talking-head candidate**, not a B-roll beat (flag it back to Stage 4 — but
   do not invent THs; usually the surrounding concrete sentence carries the shot).
4. Target **~1 clip per 6–9 s of finished video**. A 10-minute video is ~70–100
   beats. This is the expected volume — plan waves and scheduled continuation
   accordingly (Stage B3).

## Stage B2 — write the iPhone B-prompt for every beat

Full doctrine + examples: `references/iphone-broll-doctrine.md`. Every beat
prompt is **Mode B (no character on screen)** and obeys the parent's 7-component
contract and all of `references/veo-prompting.md`. The four non-negotiables that
make it Elias-Yoder rather than generic AI B-roll:

1. **Quote the sentence at the top of the prompt** (as a comment to yourself),
   then build the shot around the ONE concrete noun + action the viewer's eye
   should land on. The clip must depict THAT, literally — not the topic, the
   sentence. ("a four-dollar strip of cotton muslin nailed under the rafters" →
   hands tacking a muslin strip under bare attic rafters; NOT "a cozy attic").
2. **The iPhone token block** (verbatim, every prompt): *shot on a modern
   smartphone, deep focus with everything sharp, wide ~26 mm-equivalent lens,
   natural available light, slight handheld micro-shake, true-to-life color,
   crisp fine detail, no bokeh, no film grain, no cinematic color grade.* This
   REPLACES the parent's "35 mm / shallow depth of field / film grain" tags.
   Most clips are this default handheld tier; reserve the steadier "phone propped
   on a surface" tier for a minority of hero establishing shots (see doctrine).
3. **Hands-at-work are HERO shots here, not artifacts.** Elias's most authentic
   shots are close, slightly-clumsy hands doing the practical thing (tacking the
   muslin, prying the gable vent, lighting the lamp). The parent banned
   disembodied hands; this skill ALLOWS and engineers them — with a consistent
   "weathered hands, plain rolled sleeves" continuity tag — because they are the
   single strongest "a real person made this" signal. Keep the motion a single
   slow arc (no fast fine-finger work, which Veo mangles).
4. **The continuity bible** (the locked world block for THIS video) is injected
   verbatim into every prompt so all ~80 clips read as one place. See Stage B-cont.

Run the **period-authenticity panel** (`references/period-authenticity-panel.md`)
on every prompt before it is queued: it strips anachronisms (power lines, light
switches, outlets, cars, phones, plastic, visible buttons/zippers, modern
fixtures) and the standard AI tells (warped hands, morphing text on tools, extra
fingers, impossible physics). In this niche a wrong-period object is as fatal as
a glitched hand.

## Stage B-cont — continuity across dozens of clips (the "same place" problem)

Eighty separately-generated clips of "the farmhouse attic" will look like eighty
different attics unless continuity is engineered. Full method:
`references/beat-segmentation-and-continuity.md`. Three locked mechanisms:

- **The continuity bible (text anchor).** Before generating, write a fixed
  canonical block for this video — the farmhouse, each recurring location (attic,
  summer kitchen, root cellar, barn), the season, the time of day, the light, the
  color palette, and the recurring "hands + plain clothing". Store it in the
  manifest and paste it **verbatim, unchanged** into every beat prompt (only the
  shot/action varies). This is the cheapest, highest-leverage lever — do it always.
- **Anchor keyframes (image anchor).** Generate the few recurring *locations*
  FIRST as establishing shots, capture a clean frame from each, and attach that
  frame as the **first-frame keyframe** for every later beat set in that location
  (headless attach per `references/69labs-video-workflow.md` Recipe 1). One attic
  frame anchoring all attic beats keeps the rafters, the light, and the wood tone
  identical. This is on by default for any location used in ≥3 beats.
- **Last-frame → first-frame chaining (motion anchor).** For two beats that
  should read as one continuous moving shot (a slow walk toward the gable vent),
  feed the previous clip's LAST frame as the next clip's first-frame keyframe.
  Use sparingly — only where the script genuinely wants a continuous move.

## Stage B3 — generate in waves of 5 (69labs)

The account can run **up to 5 concurrent video jobs via the API** — use it.
`scripts/batch_generate.py` is the resumable client: it reads the beat-prompt
manifest, submits up to 5 jobs at a time, polls the jobs API, captures each
finished clip via its `directFileUrl`, and updates the manifest after EVERY job
(so a VM reset or rate-limit pause resumes cleanly).

```bash
python3 scripts/batch_generate.py \
  --manifest broll_manifest.json \
  --concurrency 5 \
  --model "Veo 3.1 Lite" --aspect 16:9 \
  --out-dir "<video folder>/Source clips/broll"
```

- **Respect the account's real quota.** The browser-observed caps are 10/hour
  and 100/month; confirm the API's own caps before a big run. An ~80-beat video
  WILL exceed an hourly cap — so the client generates what the window allows,
  marks the rest `pending`, and you **offer the user a scheduled hourly task** to
  drain the queue (exact prompt in the parent skill's Stage-6 wording, adapted:
  "continue the AI B-roll batch for video N from broll_manifest.json"). Progress
  is monotonic; nothing regenerates.
- **Keyframes** (continuity): when a beat has an `anchor_keyframe` or a
  `chain_from` set, the client uploads/sets it via `/api/videos/upload` +
  composer localStorage (Recipe 1) before submitting that job; pure-B beats with
  no anchor verify `KEYFRAMES 0/2`.
- **Confirm the submit path against the user's 69labs API.** The capture
  (`/api/jobs` + `directFileUrl`) and keyframe-upload (`/api/videos/upload`)
  endpoints are field-verified; the job-CREATE call is the one place to confirm
  against the account's API docs. `batch_generate.py` isolates it in one
  `create_video_job()` function with the documented composer payload as the
  default — adjust only that function if the account's create endpoint differs.
- Watch the FIRST clip of the run end-to-end before continuing: iPhone look
  present, no bokeh/grain, no subtitles, period-accurate, depicts the sentence.
  Fix the token block once, not after 80 bad clips.

## Stage B4 — trim to beat, place, concat the body segment

B-mode beat clips carry **no dialogue** (the narration runs over them), so the
clip's own Veo audio is discarded. Each clip is 8 s; each beat is 6–9 s:

```bash
python3 scripts/trim_and_place.py --beats beats_<n>.json \
  --clips-dir "<...>/broll" --narration body_<n>.mp3 --out body_<n>.mp4
```

- A beat **shorter** than 8 s → trim the clip to the beat length (keep the most
  on-action middle; avoid the inhale-y final 0.3 s).
- A beat **longer** than 8 s → it should already have been split into two beats
  in Stage B1; if a single 8 s clip must stretch, prefer generating a second
  chained clip over slow-motion (slow-mo reads as fake). Never freeze-hold a
  frame to fill time — a held frame is an instant "AI" tell.
- Lay the trimmed clips end-to-end over the segment's narration MP3 → `body_<n>.mp4`.
  No clip plays back-to-back with an identical one; vary camera setup and angle
  across adjacent beats deterministically (`pool[(beat_i*7) % len(pool)]`).

Then hand `body_<n>.mp4` to the parent's Stage 8 assembler exactly like any body
segment.

## Stage B5 — gates specific to this skill (add to the parent's Stage 9)

Run the parent's Stage 9 gates, and ADD these — they are the failure modes of an
all-AI B-roll video:

1. **Sentence-match gate.** For each beat, the placed clip must depict its
   verbatim sentence's concrete noun/action. Spot-check ~10% of beats (sample the
   first-half densely): pull the beat's middle frame, read it against the
   sentence — a thematically-adjacent shot is a FAIL, regenerate with a tighter
   prompt. This is the single most important quality bar.
2. **iPhone-look gate.** No clip may show cinematic bokeh, film grain, a teal-
   orange grade, or a tripod-smooth crane move. Any clip that looks "produced"
   fails — regenerate with the token block re-pinned. (A minority of steadier
   hero shots is allowed; a *cinematic* one is not.)
3. **Period/anachronism gate.** Scan sampled frames for power lines, switches,
   outlets, cars, phones, plastic, modern fixtures, visible zippers/buttons. Any
   hit fails the clip — regenerate.
4. **Continuity gate.** Eyeball that recurring locations look like the SAME place
   across their beats (attic wood tone, light direction, color palette stable).
   Drift → the bible wasn't pinned or the anchor keyframe wasn't attached; fix
   and regenerate the drifted clips.
5. **Rhythm gate (inherited intent).** Assert the assembled order still alternates
   body ↔ character insert (the parent's structural check) — i.e. the
   B-roll-interrupted-by-talking-head cadence is intact. THs weighted to the
   first half (3+1 default).

Deliver per the parent's Stage 9: final `<TITLE>.mp4` + every generated clip
separately (hook, CTA, each talking head, and **each AI B-roll clip**, named
`AI B-roll NN — <short sentence>.mp4`), the description, and the manifest. Then
run Stage 9.5 finalize.

## Manifest additions

Extend the parent's `ultimate_manifest.json` with a `broll` block (single source
of truth for the body engine; `batch_generate.py` reads/writes it):

```json
{
  "broll": {
    "continuity_bible": "verbatim world block injected into every B prompt",
    "anchor_keyframes": {"attic": "broll/anchor_attic.jpg", "cellar": "..."},
    "beats": [
      {"id": "b1-03", "segment": "body-1", "start": 18.2, "end": 25.1, "dur": 6.9,
       "sentence": "He nailed a four-dollar strip of cotton muslin under the rafters.",
       "prompt": "…full iPhone B-mode Veo prompt…",
       "anchor_keyframe": "attic", "chain_from": null,
       "status": "pending", "file": null, "job_id": null, "generated_at": null}
    ]
  }
}
```

`status` advances `pending → generated → placed → done`. The `beats` list IS the
wave ledger and the resume point.

## Bundled files

- `references/iphone-broll-doctrine.md` — the Elias-Yoder B-roll aesthetic: the
  iPhone token block, the two shot tiers, hands-as-hero, the literal-match rule,
  the "real person made this" principle, and worked B-prompt examples. Read first.
- `references/beat-segmentation-and-continuity.md` — cutting narration into 6–9 s
  beats + the three continuity mechanisms (bible, anchor keyframes, frame chaining).
- `references/period-authenticity-panel.md` — the niche reality gate (anachronism
  + AI-tell list) run on every prompt and sampled frame.
- `references/veo-prompting.md` — Google's Veo 3.1 rules (inherited; obey on every prompt).
- `references/69labs-video-workflow.md` — field-tested 69labs mechanics (keyframe
  attach, directFileUrl capture, quota, outage handling).
- `scripts/segment_beats.py` — force-align a body narration + cut it into 6–9 s
  sentence-beats → `beats_<n>.json`.
- `scripts/batch_generate.py` — resumable 69labs client: waves of up to 5
  concurrent jobs from the beat manifest, keyframe attach, directFileUrl capture.
- `scripts/trim_and_place.py` — trim/pad each beat clip to its beat length and
  concat into `body_<n>.mp4` over the narration.
- `scripts/verify_broll.py` — the Stage B5 gates (sentence-match sampling,
  duration match, duplicate/back-to-back check, period-flag frame scan).

---

# v2 field fixes (69labs public API; consistency, realism, A/V sync)

These updates fix issues seen on a real all-AI build (the Candice candle channel).
The reference engine is in `scripts/generate_69labs_v1api.py` (generation) and
`scripts/assemble_segmented_v2.py` (assembly). New doctrine:
`references/comprehensive-prompt-system.md` — read it before writing prompts.

## 69labs PUBLIC API contract (use this, not the browser paths)
- Base `https://69labs.vip/api/v1`; auth `Authorization: Bearer vk_...`.
- Lifecycle for all media: `POST .../generate` → `GET .../{type}/status/{id}` →
  `GET .../{type}/download/{id}` (302 → presigned; follow redirects).
- Video model: `veo-video` ("Veo 3.1 Lite"), 8s clips, 16:9, `imageUrls` for
  keyframes/ingredients, **max 5 concurrent jobs** (wave-schedule to ≤5).
- TTS: `POST /tts/generate` with `voiceProvider` `edgetts` or `elevenlabs` + a
  valid `voiceId`; poll `/tts/status`, download `/tts/download`.
- **Always send a browser `User-Agent`** — the default `Python-urllib` UA is
  Cloudflare-blocked (error 1010) and every call fails.

## Face consistency — reference image on EVERY clip
Attach the locked reference to all jobs: `keyframes` mode for character shots,
`ingredients` mode for B-roll. Host the reference on a STABLE URL (a file
committed to a public repo and served via `raw.githubusercontent.com`), never an
expiring temp host — if the URL dies mid-run, every later clip fails.

## Realism — the five-block prompt
Every prompt = ACTION (name every object + the complete physical action) + iPhone
camera block + person-consistency line + world bible (verbatim) + realism/negative
clause. This eliminates "poured into nothing" and "wick cut without contact". See
the new reference doc.

## A/V sync — kill segment drift (talking-head lip desync)
Cause: per-segment audio length ≠ video length, so the concat demuxer accumulates
drift and later talking-head voices lead the lips. Fix (in
`assemble_segmented_v2.py`): render every segment to identical specs (1280x720,
24fps CFR, AAC 48k stereo) and force each segment's audio to EXACTLY equal its
video length (`aresample=async=1`, `apad`, `atrim=0:D`); character beats keep
their native Veo speech locked to their own video length; final concat re-encodes
with `+genpts`/CFR. Verify: assembled video and audio stream durations match.

---

# Delivery SOP — per-video deliverable package (zip)

Every finished video ships as ONE zip named for the video, containing exactly:

```
<Title>_deliverable.zip
├── <Title>.mp4          # the final assembled video (full quality)
├── description.txt      # YouTube description with chapter timestamps
├── thumbnail.png        # 1280x720 thumbnail (see thumbnail SOP below)
└── Source clips/        # every generated clip (hook, talking heads, all B-roll)
```

Build it with `scripts/build_deliverable.py <video_folder>`; deliver the zip (host
it and give the link — large zips exceed chat/GitHub limits).

## Thumbnail SOP — generate with GPT Image 2
Generate the thumbnail with the **`gpt-image-2`** image model on 69labs, using the
**"Thumbnail Prompt"** column from the channel content sheet for that video row
(the sheet's prompt is authored in the SUBJECT / FOCAL OBJECT / TEXT OVERLAY /
COLOUR / ANNOTATIONS / BACKGROUND / COMPOSITION / LIGHTING / DO NOT INCLUDE /
aspect / style format). Pass the channel reference photo as `imageUrls` for
character likeness, `aspectRatio: "16:9"`. If gpt-image-2 is unavailable, retry,
then fall back to a clip frame + text overlay. Always include a thumbnail in the
deliverable package, even when the user says it isn't needed this once.

---

# Long-run progress loop & keep-alive (SOP)

Big videos generate for an hour or more across quota windows. Keep the session
awake and the user informed on a fixed cadence:

- **Preferred (if available): a scheduled task / wakeup** every 10 min that checks
  progress and posts a one-line update (`/loop 10m <check>` where cron/ScheduleWakeup
  exist).
- **Fallback (no cron): a persistent `Monitor`** running a `while true; … ; sleep 600`
  loop that **emits one status line every 10 minutes** — each line is a chat event
  that both updates the user and keeps the session from going idle. The loop must:
  1. count downloaded clips vs total (from `state.json`/`manifest.json`),
  2. echo `progress: <done>/<total> … <last finish.log line>`,
  3. detect the terminal marker (e.g. `VIDEO4 ASSEMBLED`) and emit a final line +
     `break` so the watch ends,
  4. cover stalls — it reports every 10 min regardless, so a frozen count is visible.
- Pair it with a **finish/auto-resume chain** (`while pgrep generate; do sleep; done`
  → if clips remain, wait for the hourly credit reset, resume `generate.py`, repeat →
  then `assemble.py` → emit the terminal marker). This rides through the 100/hr cap
  unattended.
- On the terminal marker: verify the final mp4 (video & audio stream durations
  match), build the deliverable zip (`scripts/build_deliverable.py`), host it, post
  the link, and stop the monitor (`TaskStop`).
