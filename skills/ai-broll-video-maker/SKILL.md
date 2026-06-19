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

### Hosting / upload — ALWAYS sanitize the filename first (hard-won lesson)
File hosts (litterbox/catbox/gofile/0x0/bashupload) are uploaded via
`curl -F fileToUpload=@<path>`. **curl's `-F` field chokes on paths containing
spaces, commas or other special characters** — it fails with `curl (26) Failed to
open/read local data` and returns an EMPTY body. Because our deliverables are named
for the video title (e.g. `POOR SCENT THROW - ... , This Is The REAL Issue.zip`),
uploading that path directly **fails silently** and looks exactly like a
size/network limit — leading you to wrongly "discover" a ~80MB upload cap and waste
time splitting files. There is NO such cap: with a clean filename, full 100–300MB
files upload in seconds.

THE FIX (already baked in): **copy to a sanitized temp name before uploading.**
- Use `scripts/host_upload.py <file> [<file> ...]` — it sanitizes the name, uploads,
  retries, and verifies the hosted `content-length` matches the local size.
- Or just run `scripts/build_deliverable.py <video_folder> --host`, which builds the
  zip and then hosts the **zip + final mp4 + thumbnail**, printing one link each.

So the standard end-of-generation delivery is a single command:
```
python3 scripts/build_deliverable.py <video_folder> --host
```
which prints, e.g.:
```
DELIVERABLE: .../<Title>_deliverable.zip (252 MB)
LINK: <Title>_deliverable.zip -> https://litter.catbox.moe/xxxx.zip  [verified]
LINK: <Title>.mp4            -> https://litter.catbox.moe/yyyy.mp4  [verified]
LINK: thumbnail.png          -> https://litter.catbox.moe/zzzz.png  [verified]
```
Give the user the **single-file zip link** as the primary deliverable. Never hand
back split parts unless a host genuinely rejects a verified-clean filename.

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

---

# FORMAT: talking-head ↔ literal phone-cam B-roll (informational, not tutorial)

The channel's default format. ONE continuous channel-voice narration runs the whole
video; the VISUAL track alternates between TALKING_HEAD (the presenter anchor, on
camera) and B_ROLL (footage that LITERALLY depicts the concrete noun the narration
is saying at that instant, shot to look like casual phone-cam footage). The cut
follows the NOUN: "you walk down the aisle" → POV down a grocery aisle; "you pick up
the baking soda" → phone shot of a hand grabbing a baking-soda box. Abstract/claim
lines are delivered ON camera (talking head); concrete noun+verb lines are SHOWN.
The character appears ONLY in talking heads — never in B-roll. Less tutorial, more
informational.

## Beat schema (segment the script into these)
`{ text, t_start, t_end, visual_subject, visual_action, shot_type(POV|hands|wide|reaction|hero), abstract }`
Split at sentence/clause boundaries; a new concrete subject = a new beat (so "aisle"
and "baking soda" are two beats → two cuts). B_ROLL beats are SHORT (2–5s), cut on
the noun.

## Visual-type scheduler (config knobs at top of build)
`talking_head_ratio=0.40  max_th_run_s=10  max_broll_run_s=25  th_mode=sync|pool
 pool_size=8  broll_beat_target_s=3  hook_archetype=auto|price-wall|crisis|sensory-siege|inventory|reframe|unbelievable`
- abstract→TALKING_HEAD; concrete→B_ROLL depicting it. Hold TH near 0.40 of runtime.
- No TALKING_HEAD run >10s (force a B_ROLL of the nearest concrete noun); no B_ROLL
  run >25s (insert a short TH anchor).
- HOOK: beat 1 = TH cold-open (presenter, ~3–6s) → hook-scenario beats = B_ROLL
  literally depicting the scenario → one TH pivot beat. OUTRO/CTA = TH.
- Never narrate a demo to camera — demos are SHOWN.
- Keep assembly constraints: no clip >2×, never back-to-back identical, never frozen.

## 7-act spine + hook archetypes (script writer)
(1) cold-open scenario → (2) pivot + honest disarmer → (3) promise + first proof →
(4) core demo/test → (5) why-it-works → (6) application stacking (long middle) →
(7) recap + soft CTA. Open with one of: price-wall · crisis-imagination ·
sensory-siege+villain · inventory-of-loss · unsettling-reframe · unbelievable-claim.
Hook = 2nd-person scenario with hyper-specific numbers/items → stakes → pivot to the
character's heritage authority → honest disarmer → cheap promise.

## B_ROLL generation = phone-cam Veo block (no corpus here → generate every beat)
Insert visual_subject+visual_action into:
```
[SUBJECT performing ACTION], filmed as casual amateur smartphone footage. Handheld
iPhone video with slight natural shake and minor reframing, eye-level or POV, natural
available light (no studio lights), an ordinary real-world setting, no color grading,
slightly flat/auto-exposed, deep focus (NO cinematic shallow depth of field), candid
vlog feel. No on-screen text, captions, watermark, logos or title cards.
```
Plus the GLOBAL physics + hyper-specific choreography rules above. No character in B_ROLL.

## TALKING_HEAD generation
Mode-A presenter (reference photo, lip-synced to that beat's exact text), same
character/costume/framing every video. th_mode=sync → fresh lip-synced clip per TH
(its own audio plays, VO ducks). pool mode (long/cheap) → reuse ~8 presenter clips as
visuals under the continuous VO, reserving exact lip-sync for hook + outro.

## QC additions (extend the gate)
TH ratio in [ratio−0.07, ratio+0.07]; no TH run >max_th_run_s; no B_ROLL run >
max_broll_run_s; literal-match audit (each B_ROLL depicts its visual_subject);
phone-cam audit (reject cinematic/drone/aerial/studio); plus existing black/freeze/
AV-skew/on-screen-text/wrong-face checks. ALWAYS output the beat-schedule table
(`beat# | t_start–t_end | type | visual_subject | source`) for review BEFORE rendering.

---

# FORMAT v2 — talking-head-dominant (~70%), gap-consolidated TTS

Refinement of the talking-head↔B-roll format toward MORE presenter, FEWER generated
B-roll clips (fewer clips = fewer AI errors). Informational, not tutorial.

## Ratios
- `talking_head_ratio ≈ 0.70`. The presenter (own lip-synced audio) carries most of
  the video. Generate a B-roll clip ONLY when it is genuinely critical to SHOW what
  is happening or what happened (the proof shot) — otherwise just say it on camera.
- B-roll is either **generic** (a plain AI clip of the thing being described, e.g.
  "someone walking down a grocery aisle" — text-to-video, no channel character) or
  **the character doing the thing** (keyframe from the reference). Keep B-roll rare.

## TTS rule (IMPORTANT — do not over-generate TTS)
Talking-head clips generate their OWN audio; never TTS them. TTS is ONLY for the
B-roll **gaps between talking heads**, and exactly **ONE TTS per contiguous gap**,
covering all of that gap's narration as a single continuous clip — NEVER one TTS per
beat. A run of three 4-second B-roll beats = ONE gap = ONE TTS, with the three video
clips placed under it. (Symptom of the bug: many ~4s TTS clips in the 69labs log.)

## Stricter talking-head generation (anti-AI-tell)
Append to every talking-head prompt: "exactly one person; a single solid subject with
no second transparent copy, no double exposure, no ghosting, no morphing, no extra or
duplicated hands/arms, natural blink and lip-sync, steady framing." On assembly, trim
the first ~1.2s of each talking-head clip (the keyframe-morph where ghosting appears).

## Assembly with gaps
- Talking-head beat → one segment (its own native audio, its own length).
- Gap (≥1 consecutive B-roll beats) → one segment: concat the gap's B-roll video clips
  trimmed to share the gap's single TTS duration; audio = that one gap TTS.
- Keeps continuous narration (TH speech + gap VO) with far fewer TTS calls.

---

# FORMAT v3 fixes — clean talking heads + automated B-roll realism gate

## 1. Talking-head ghosting (face fades into another face)
Cause: Veo morphs the reference headshot into the scene over the first ~1s.
Fix (PREVENTION): generate ONE canonical "start frame" image of the presenter in
the real set, facing camera, mouth just parted, ready to speak; commit it and use
its URL as the `th_keyframe_url` keyframe for EVERY talking-head clip. Every TH then
starts from the identical, in-scene frame, so there is no morph/cross-fade. Prompt:
"the very first frame is already this exact woman, sharp and in focus; NO fade-in,
dissolve, cross-fade or morph from another face." Optionally detect residual ghost
with `qc.py firstsec` (vision-review the first-1.2s contact sheet).

## 2. Bad talking-head→talking-head transitions / double breath
Cause: each clip ends with an inhale and the next begins with another inhale, and
framing jumps. Fix: (a) same canonical start frame → consistent pose/framing so
clips line up; (b) prompt "she is already mid-conversation: begins the first word
immediately with NO inhale or pause at the start, speaks continuously, no big inhale
at the end"; (c) assembler trims leading/trailing SILENCE per TH clip
(`speech_bounds()` via silencedetect) so seams flow — never trims speech.

## 3. Freeze-frame under voiceover
Cause: a near-static clip held under VO. Fix: `qc.py freeze` (ffmpeg freezedetect)
flags any frozen span ≥0.6s; prompt every clip for "continuous subtle handheld
camera motion and real movement; the frame is NEVER static or frozen"; regenerate
flagged clips. Talking heads must always be in motion.

## 4. Automated B-roll realism gate (frame-by-frame, retry ≤2)
Pipeline per B-roll clip:
  1. `qc.py contactsheet <clip> sheet.jpg 6` → 6 evenly-spaced frames tiled.
  2. `qc.py freeze <clip>` → freeze verdict.
  3. JUDGE: a vision-capable subagent (the Agent tool) reviews the contact sheet and
     returns realistic? + reason (looks for AI tells: warping, melting edges, extra
     fingers, impossible physics, plastic/uncanny look, gibberish, wrong objects).
  4. If FREEZE or NOT-realistic → `regen_clip.py <proj> <beat_id> --stronger`
     (re-generates with an escalated realism+continuous-motion clause), then re-judge.
     Retry up to 2 times; after that keep the best take and flag it.
Scripts: `scripts/qc.py`, `scripts/regen_clip.py`. The judge is the Agent tool (no
standalone vision API here); swap in a vision LLM call for a fully hands-off loop.
Note: inherently static "result" hero shots will always trip freezedetect — give
them camera drift in the prompt rather than treating stillness as a failure.

---

# FORMAT v4 — frame-chaining + lip-sync gate + audio master (the consistency stack)

Run all four on every new video:
1. **Talking-head frame-chaining** (`scripts/generate_chained.py`): consecutive TH
   beats form a RUN; clip 1 starts from `th_keyframe_url`, each next clip's keyframe
   is the previous clip's LAST FRAME (extracted + hosted). The run becomes one
   continuous take — verified seamless. Runs generate concurrently; within a run
   sequential. B-roll parallel; one TTS per gap.
2. **Lip-sync / script gate** (`scripts/lipsync_gate.py <proj> --fix`): transcribe
   each TH, fuzzy-match to its scripted line, regenerate mismatches (<=2).
3. **Realism gate** (`scripts/qc.py` + vision subagent judge + `scripts/regen_clip.py`):
   per B-roll clip extract a contact sheet + freeze verdict, a vision subagent rules
   realistic?/reason, failures regenerate with the escalated realism+motion clause (<=2).
4. **Audio master** (`scripts/master_audio.py <in> <out>`): two-pass loudnorm to
   -16 LUFS, high-pass + light denoise, faint room-tone bed; run on the final cut.

Order: generate_chained -> lipsync_gate --fix -> realism gate (regen) -> assemble
(gap-aware, silence-trim seams) -> master_audio -> deliverable zip.

# FORMAT v5 — short chains + scene rotation + cloned voice (consistency, refined)

Builds on v4. The build script now emits `manifest["chains"]` (the generator consumes
them directly instead of computing runs):

1. **Max 3 TH clips per chain.** Longer TH stretches split into chains of <=3, so
   identity/quality drift can only compound twice. Lets us use the EXACT last frame.
2. **Exact-last-frame chaining** (`host_frame`): grab the literal final frame (-sseof
   -0.04) for perfect seam continuity, with a near-black fallback (step back if the
   final frame is a fade). No more 0.33s pose-rewind from the old -0.35 grab.
3. **Scene rotation ONLY on direct TH->TH jump-cuts.** Default scene = workbench. When
   a contiguous TH run is split (no B-roll between), the new chain seeds from a
   different SCENE ANCHOR (bench -> kitchen/stove -> curing shelf, rotating) and its
   first clip gets a "moved to <scene>, settling, mild movement" beat, so the cut reads
   as an intentional location change. After B-roll she returns to the bench. Scene
   anchors are committed reference PNGs (`video_*/assets/*.png`) used as keyframes.
4. **B-roll = the character's own hands in her workspace.** B-roll seeds from a
   committed `hands_ref` image (her hands, her sleeves/apron, her bench) via
   `videoInputMode:keyframes`; never generic text-to-video. Consistent skin/space.
5. **Labels allowed on talking-head (static) shots, off motion B-roll.** Veo renders
   short printed jar labels fine on near-static TH backgrounds but garbles text in
   motion — so TH prompts allow simple labels, B-roll/motion prompts forbid text.
6. **Cloned-voice TTS via the Voice Clones API.** Cloned voices are NOT usable through
   `/tts/generate` (that validates against the MiniMax *catalog* and rejects clones).
   Use `POST /api/v1/voice-clones/generate` with `voiceCloneId` (UUID from
   `GET /voice-clones`), `model` (e.g. speech-2.8-hd), and `speed` (0.5-2.0 multiplier,
   1.0=normal). Poll/download via the standard `/tts/status|download` endpoints.
   NOTE: talking heads still speak in Veo's own generated voice (needed for lip-sync);
   the cloned voice drives only the B-roll gap narration.

## Audio drift fix (assembler)
Per-clip lip drift came from per-segment dynamic `loudnorm` (uncompensated lookahead
latency) + missing `async`. Fix: level each segment with a **static gain**
(volumedetect -> `volume=NdB`, zero latency), lock audio length to video length
(`aresample=async=1:first_pts=0` + `apad,atrim=0:D`), and leave the single global
loudness pass to `master_audio.py`. Never per-segment dynamic loudnorm.

## Thumbnail
Always pass the channel character reference photo as `imageUrls` to a model that
supports image input. NOTE: gpt-image-2 FAILS with `imageUrls` here — use
`nano-banana-2` for character-referenced thumbnails (gpt-image-2 only when prompt-only,
and prompt-only invents a generic stranger — it did once, a man).

# FORMAT v5.2 — review-driven polish (identity, seams, color, watermark, audio, scenes)

From a detailed user review of a v5 cut. All baked into build_ps.py / generate_chained.py /
assemble.py / lipsync_gate.py / gen_anchors.py:

1. **Seam = position, not just color.** Verified: chained clips' seed frames DO match
   (clip N last frame ≈ clip N+1 first frame). The visible position pop came from the
   assembler trimming silence at EVERY seam, cutting the matched frames. FIX: trim only
   the chain's FIRST-clip leading silence and LAST-clip trailing silence; inter-clip
   seams play full so the matched frames butt together. (`chain_start`/`chain_end` sets.)
2. **Color-lock.** Even matched seams drift ~5% in brightness/white-balance because Veo
   grades each clip independently. FIX: measure each clip's mean Y/U/V, shift (static
   `lutyuv`) toward the global median so same-scene clips match. (Color is a SECONDARY
   cause; the seam-trim above is the primary one.)
3. **Veo watermark** — REMOVE IT NATIVELY VIA THE API, do NOT crop. The video generate
   endpoint takes `skipWatermarkRemoval` (default false = FastGen watermark cleanup ENABLED
   for eligible Veo/Gemini outputs). Always send `skipWatermarkRemoval: false` on every
   `/videos/generate` (and regen) call so all clips come out watermark-free at full frame —
   no crop, no zoom, no off-centre offset. (Cropping was the old workaround and caused
   off-centre framing; only fall back to a CENTERED final crop if native cleanup is ever
   unavailable.)
4. **B-roll VO too quiet vs talking heads.** mean-volume leveling was perceptually off.
   FIX: static gain to a common INTEGRATED-LUFS target (`loudnorm` analysis only → static
   `volume`), timing-safe; final polish still by master_audio.
5. **Wrong avatar on TH clips = identity drift.** ALWAYS seed every TH clip from a Candice
   reference image (chain-start = clean scene anchor; continuation = previous Candice
   last-frame) and lead the prompt with an explicit "EXACT SAME woman as the reference,
   do not change her face" clause. regen_clip.py also seeds TH from the chain's scene
   anchor (never text-to-video) so fixes can't introduce a stranger.
6. **Clean, labeled, ready-to-speak anchors + 5-scene rotation.** Scene anchors must have
   NO signs/REC/UI/viewfinder outline (those propagate into clips), jars LABELLED, and the
   subject framed ready to speak. Scenes: bench(default)→kitchen→shelf→packing→window,
   rotated on direct TH→TH jump-cuts only. B-roll seeds alternate hands_ref / overhead_action.
   Generate the whole anchor set in PARALLEL (submit all, then poll) — the image backend can
   be slow. Deliver the anchor set as a zip for the user to keep.
7. **Lip-sync gate is noisy → 3x consensus.** whisper(base.en) gives disjoint failure sets
   run-to-run. A clip only FAILS if it fails a majority of up to 3 transcriptions; never
   regenerate on a single low score (wastes credits on good clips).

# FORMAT v5.3 — face gate, hard no-text, crossfade transitions (a wrong face can NEVER ship)

1. **STRICT per-section FACE GATE (mandatory before assembly).** Veo 3.1 Fast drifts
   identity across chains — a continuation clip can become a DIFFERENT person (e.g. the
   packing chain once drifted to a different woman). So every TH and B-roll section is
   verified to be the channel character BEFORE assembly:
   - `scripts/face_gate.py <proj> --list` extracts 2 frames per section and prints JSON.
   - The parent hands each batch + the reference photo to a **panel of vision sub-agents**
     (Agent tool) that returns MATCH / MISMATCH per section (strict: MATCH only if clearly
     the same woman; B-roll hands-only clips pass if no WRONG person appears). Run several
     agents in parallel for speed.
   - `scripts/face_gate.py <proj> --regen id1,id2` regenerates mismatches (regen_clip seeds
     TH from the section's clean scene anchor, B-roll from its hands ref).
   - LOOP list→judge→regen until **every** section is MATCH. Only then assemble. A wrong
     face must never reach the output. (No face-recognition lib is installed here; the
     vision-agent panel is the accuracy/efficiency sweet spot. If `face_recognition`/
     `insightface` is ever available, use embedding distance as a fast pre-filter.)
   ROOT CAUSE of drift: chaining continuation clips off a previous (already-drifting) frame.
   Mitigations baked in: ≤3-clip chains, clean-anchor chain starts, strong IDENTITY prompt
   ("EXACT SAME woman ... do NOT change her face/age/ethnicity"), regen always re-seeds from
   a clean Candice anchor.
2. **HARD no-text ban.** Veo rendered spoken lines as on-screen captions. Every prompt now
   carries a NOTEXT block forbidding ALL on-screen text: subtitles, captions, transcription
   of speech, words, letters, lower-thirds, REC dot, battery/UI, timecode, watermark, logos.
   (Physical printed jar labels are explicitly distinguished as allowed, not "on-screen text".)
3. **Crossfade transitions.** Assembler supports `XFADE=<sec>` env (e.g. 0.15) → chains
   `xfade` (video) + `acrossfade` (audio) across all segments for smooth transitions instead
   of hard cuts. Total shortens by (N-1)*XFADE, so keep XFADE small (0.12–0.18) and pad the
   script length accordingly. Falls back to hard concat if the xfade graph errors.
4. **Watermark:** native API `skipWatermarkRemoval:false` on every video submit (no crop).

# FORMAT v5.4 — QUANTITATIVE face gate, talking-head CTA, smooth same-scene transitions, chaptered deliverables

The vision-agent panel (v5.3) was unreliable in both directions — it MISSED real imposters
(a recurring "imposter" Candice variant: darker, tighter ringlet curls + chunky thick-rimmed
glasses + a brighter blue cable-knit sweater) and FALSE-flagged legit wide-shot / profile /
downward-gaze Candice. v5.4 replaces eyeballing with a measured detector and adds the polish
items below.

1. **QUANTITATIVE 2-class face detector — `scripts/face_scan.py <proj> [--json out]`.**
   Uses **ArcFace embeddings** (`pip install insightface onnxruntime`, model `buffalo_l`,
   CPU). It builds TWO centroids:
   - **Candice centroid** = mean embedding of clean Candice images (the reference photo +
     the five scene anchors).
   - **Imposter centroid** = mean embedding of confirmed imposter frames committed at
     `scripts/../imposter_refs/*.jpg` (extend this set whenever a new wrong face is found).
   For each clip it samples **8 frames** (catches mid-clip drift, not just 2), detects the
   largest face (`det_score>0.55`), and per frame computes `sim_candice` and `sim_imposter`.
   A frame "leans imposter" when `sim_candice - sim_imposter < -0.02`. A character clip is
   **FLAG-imposter** when ≥4 of 8 frames lean imposter; **REVIEW** when 2–3 do. B-roll flags
   only on ≥3 imposter-leaning frames.
   WHY 2-class: a single distance-to-Candice threshold cannot separate wide-shot Candice from
   the imposter — both score ~0.42–0.52, so the threshold either misses imposters (b52, b44,
   b35 all slipped a 0.44 cutoff) or false-flags wide shots. Comparing distance-to-Candice vs
   distance-to-imposter is framing-invariant and decisive (imposter clips run sim_imposter
   ~0.6–0.7 ≫ sim_candice; real Candice runs the opposite even when its absolute sim is low).
   REVIEW tier: eyeball those at **full resolution** (a small montage thumbnail once hid an
   imposter — never judge faces from tiny frames).
2. **Regen → RE-SCAN → iterate (a regen can produce ANOTHER imposter).** Re-seeding a flagged
   clip from the clean anchor reduces but does not guarantee a correct face — veo can drift
   again. So the loop is: scan → regen FLAG+REVIEW → **re-scan the regenerated clips** →
   regen anything still flagged → repeat until the scan returns 0. Never assume one regen fixed it.
3. **Robust downloads (curl + ffprobe validation).** `regen_clip.py` and `book_cta_th.py`
   download with `curl --retry 6 --retry-all-errors` then validate with ffprobe — urllib hit
   `IncompleteRead` on the 69labs CDN and left **corrupt** clips (0-frame files that look
   "downloaded"). Always re-validate. Also: a COMPLETED veo job can be unservable — if curl
   keeps returning a short/invalid file, submit a FRESH job rather than re-fetching the old id.
4. **Generator TTS crash-proofing (`generate_chained.py`).** The cloned voice can take >3 min;
   the old code polled a fixed window then DOWNLOADED a still-PROCESSING job → HTTP 400 →
   unhandled crash that stalled a whole video. Now: poll longer, only download on COMPLETED,
   wrap the download, and retry slow/`DUPLICATE_TTS_IN_PROGRESS` gaps a few times.
5. **Some B-roll prompts make veo FAIL repeatedly** (e.g. "deep sinkhole crater", over-specific
   defect descriptions). The generator requeues forever and the video never completes. Fix:
   simplify that beat's prompt to a clean hands-only action and re-submit. Keep B-roll prompts
   plain and physical.
6. **Talking-head book CTA — `scripts/book_cta_th.py <out> "<l1>||<l2>[||<l3>]"`.** Replaces the
   static Ken-Burns card. Candice is generated ON CAMERA holding the actual e-book, via veo
   `videoInputMode:"ingredients"` with imageUrls=[Candice ref, book-cover] (both STABLE raw URLs
   — ingredients refs must not be on expiring hosts). She holds the book up crisply in clip 1
   then **sets it on the bench** for later clips (held-book cover text blurs when she moves).
   Max 3 clips, crossfaded. Veo's own TH voice (matches the talking sections). Per-video tailored
   lines. CAUTION: veo sometimes burns the spoken line in as a caption — verify each CTA clip is
   caption-free (regen the offending clip with a strengthened no-caption prompt).
7. **Smooth same-scene transitions — `video_new_build/assemble_smooth.py <Project files dir>`.**
   Per-boundary crossfades: a ~0.12s **micro-crossfade** within a scene (consecutive clips in the
   SAME chain, which are frame-matched) hides the small seam jump without a visible dissolve; a
   ~0.40s crossfade only at scene changes / gap boundaries. (Uniform crossfades dissolved between
   near-identical same-scene frames → a visible ghost/pulse.) Env: `XFADE_IN`, `XFADE_OUT`.
8. **MrBeast-style hook (videos moving forward).** Open with one or two beats that lay out exactly
   what the video covers + a concrete reason to stay to the end (a formula, a reveal, a recipe).
   Prepend as "ACT 0" so it lands in the opening bench chain.
9. **Chaptered, CTA-first descriptions — `video_new_build/gen_description.py <proj> <build.py> <cfg.json>`.**
   Emits the YouTube description in this exact order: (1) one-sentence book CTA tying the book to
   the video topic + `🔗 https://candicescandles.com`; (2) main description; (3) **chapter
   timestamps** auto-derived from the build script's `# ===== ACT … =====` boundaries, timed from
   the assembled segment durations minus per-boundary crossfades plus the CTA splice offset;
   (4) more description; (5) hashtags. `video_new_build/package_video.sh` bundles final video +
   all source clips + thumbnail + description.txt into `<NAME>_DELIVERABLE.zip`.
10. **Slot management during post-production.** The backend allows only 5 concurrent video jobs.
    To regen / build a CTA while another video is still generating, SIGSTOP its generator (a
    stopped process still shows in pgrep so its supervisor won't relaunch; its in-flight jobs
    finish server-side and free slots), do the work, then SIGCONT. ALWAYS arm a separate
    auto-resume watcher (resume on a done-marker OR a safety-cap timeout) so a reaped task can't
    leave the generator paused. Once ALL videos are generated, slots are free and regens are fast.
11. **Environment reality.** Background processes (generators, supervisors, monitors) get reaped
    on container idle/restart; nothing survives a multi-hour idle. A self-healing watchdog
    (`video_new_build/watchdog.sh`) relaunches any dead piece every ~10 min while the session is
    active — but the reliable path to finishing long jobs is periodic user check-ins, each of
    which wakes the session and heals everything.

# FORMAT v5.5 — the 8-SECOND TRUNCATION gate (clips must say their WHOLE line)

veo TH clips are hard-capped at 8s. A sentence too long to say in 8s is TRUNCATED
MID-SENTENCE by veo at generation (the clip ends while she's still talking) — the
assembler faithfully keeps the whole clip, so the missing words were simply never
generated. This is invisible unless you transcribe. Hard rules now:

1. **Segment to fit 8s.** Keep each TH beat's sentence to ~18 words max (≈ what fits
   in ~7s of speech). Longer multi-clause sentences and MrBeast hooks (35-40 words)
   WILL be cut. Split them into separate beats at build time.
2. **TRUNCATION GATE (mandatory, like the face gate).** After generating TH clips,
   transcribe each SOURCE clip (faster-whisper base.en) and compare to the intended
   line; flag any clip missing its ending. Number/spelling artifacts ("fifty"->"50",
   "one"->"1") are false positives — verify by eye. `video_new_build/cutdetect`-style
   logic. Re-segment + regenerate every truncated beat before assembly.
3. **Splitting an over-long beat after the fact:** `video_new_build/split_fix.py` does
   manifest surgery — splits beat `bNN_th` into `bNN_th`(part1) + `bNNs_th`(part2) with
   a derived id so NO other beat ids shift (no cascade/regeneration of clean clips),
   and adds part2 to the same chain (same-scene micro-crossfade). Longer videos are
   fine; preserve content rather than truncating wording.
4. **OVERRUN at the split seam.** If part1 (S1) is much shorter than 8s, veo FILLS the
   remaining seconds by continuing into part2's words -> the seam STUTTERS/duplicates.
   Fix: append a hard-stop to part1's prompt — "After she says that exact sentence she
   immediately stops talking, closes her mouth, and pauses silently for the remaining
   seconds; she does NOT continue or add words." Re-gen part1. Detect overruns by
   checking whether part1's transcript contains part2's opening words.
5. **PARALLEL REGEN STATE RACE (critical).** Do NOT run multiple `regen_clip.py` for the
   SAME project concurrently — each reads+writes that project's `state.json`, so
   concurrent writes LOSE updates (a clip is generated but its state entry is
   overwritten -> the assembler then silently drops it). Either regen one-project-at-a-
   time, or repair afterwards: any `Source clips/<id>.mp4` that exists but is missing
   from state -> rewrite its state entry (status=downloaded, file=abspath). ALWAYS
   re-verify (truncation + face) the repaired beats — they were skipped by gates that
   key off state. Parallelism across DIFFERENT projects is safe.
6. **Chapters after splitting:** `gen_description.py` maps acts to ORIGINAL (non-`s_th`)
   beats so timestamps stay correct even though the manifest has extra split beats.
7. **End-to-end verification before delivery:** transcribe the FINAL assembled video's
   hook/transitions and confirm sentences play complete with no stutter — the source
   gate plus this final pass together guarantee nothing was cut or duplicated.
