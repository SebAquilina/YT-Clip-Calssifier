# Image Visuals — the Elias-Yoder "images that describe what's said" track

This adds a THIRD visual track to the channel alongside talking-head clips and hands
B-roll: **images that literally depict what the narrator is saying**, on screen for a
few seconds each. Used well, this is the single biggest lever for retention and pace,
and it **significantly reduces the talking-head share** (you no longer need her face on
screen for every sentence — her voice carries it while the image shows it).

> Doctrine (same as the B-roll doctrine): the image must be LITERALLY of the thing being
> said at that instant, not thematically near it. "She mentions a sinkhole" → an image of
> a candle with a sinkhole, not a generic candle. Literal + on-aesthetic = the channel.

---

## 0. The new visual mix (talking head reduced)

Old mix was ~70-90% talking head. New target mix per finished minute:

| Track | Old | NEW target | Role |
|---|---|---|---|
| Talking head (full) | 70-90% | **30-40%** | hook, key claims, personality, transitions, CTA |
| Image — full-frame | 0 | **20-30%** | "look at exactly this", reveals, comparisons |
| Image — split (TH + image) | 0 | **15-25%** | explaining WHILE showing; keeps her present |
| Image — come-to-life | 0 | **5-15%** | hero/beauty beats, dramatic reveals, the hook |
| Hands B-roll | 10-20% | **10-15%** | her doing the physical action |

Pacing rule: **change what's on screen every 3-6 seconds.** Never hold one mode for more
than ~12s except a deliberate talking-head moment. Vary the modes — don't run three
full-frame images back to back; alternate full ↔ split ↔ live ↔ TH ↔ B-roll.

---

## 1. The three image modes

### A. FULL-FRAME image (Ken Burns)
A still fills the whole 16:9 frame for 2-4s while the cloned-voice narration describes it.
Slow continuous **zoom in or out + slight pan** (Ken Burns) so it never feels dead.
- **Audio:** cloned-Candice TTS narration (gap-style), over the muted still.
- **Use when:** the narrator says "look at this / here's exactly what I mean", a reveal, a
  single hero object, a labelled comparison, a before/after, a number/stat callout.
- **Duration:** 2-4s (one sentence or clause).

### B. SPLIT-SCREEN (talking head + image)
The talking-head clip is cropped to one pane (default LEFT, ~46% width) and the image
fills the other pane (default RIGHT, ~54%), with a subtle Ken Burns on the image pane.
- **Audio:** the TALKING-HEAD clip's own (veo) voice — she's on screen speaking, the image
  supports her in real time.
- **Use when:** she's actively explaining and you want to KEEP her present (continuity,
  authority, emotion) while still showing the thing. Great for "as I explain X, here's X".
- **Duration:** 4-8s (a full talking-head clip's length).
- **Layout:** TH left / image right is the default (the eye reads her, then the proof).
  Mirror occasionally (image left / TH right) for variety. Keep her face centred in her pane.

### C. IMAGE COME-TO-LIFE (img2video)
An input image is used as the **first/reference frame** and veo animates it so the still
"comes to life" — the flame flickers, steam rises, the camera pushes in, light shifts.
- **Audio:** cloned-Candice TTS narration over it (muted veo audio), like full-frame.
- **Use when:** a striking/beauty/hero still benefits from motion — the hook, a dramatic
  reveal, an emotionally resonant beat. Highest production value; use sparingly so it stays special.
- **Duration:** 2-6s (trim the 8s veo clip to the beat).
- **Source image:** either a generated still (nano-banana-2) OR a real photo the user supplies.

---

## 2. WHEN to use which — the scheduler (decision rules)

Tag every body sentence-beat with a `visual_mode`. Decision order:

1. **Is it the hook / a dramatic reveal / a beauty beat?** → `image_live` (come-to-life).
2. **Does the sentence point at one concrete thing to SEE right now** ("here's a wet spot",
   "this is what a sinkhole looks like", "$2 vs $20") **and her face isn't needed?** →
   `image_full`.
3. **Is she explaining a concept/relationship where her presence adds authority/continuity,
   AND there's a thing to show?** → `image_split`.
4. **Is it a physical action she performs** (pouring, trimming, stirring)? → `broll` (hands).
5. **Is it personality / a strong claim / a transition / a direct-address line / the CTA?**
   → `talking_head` (full).
6. **Abstract line with no image and no action** → `talking_head`.

Rhythm guardrails on top of the rules:
- Open on a strong hook (`image_live` or `talking_head`), then get an image on screen within
  the first ~10s.
- After any 8-10s of continuous talking head, force a visual (image/split/broll).
- Don't repeat the same mode more than twice in a row.
- Put a `talking_head` beat at every major topic transition (re-anchors the viewer on her).

---

## 3. Beat schema additions

Extend each beat in the manifest:

```json
{
  "id": "b14_img", "type": "image", "visual_mode": "image_full",
  "sentence": "This is what a sinkhole actually looks like.",
  "image_prompt": "<literal still prompt, see §4>",
  "image_ref_url": null,                // a real input image (for split/full/live) if provided
  "kenburns": {"dir": "in", "zoom": 0.10},   // in|out, total zoom over the beat
  "split": {"th_side": "left", "th_frac": 0.46},  // only for image_split
  "motion": "the candle flame flickers gently, faint wisp of smoke, slow push-in",  // image_live only
  "narration_source": "tts",            // tts (full/live) | th_audio (split)
  "dur": 3.2
}
```
- `type:"image"` with `visual_mode` one of `image_full | image_split | image_live`.
- For `image_split`, the beat ALSO needs a talking-head clip (generate it like a normal TH beat);
  the image is composited beside it.
- For `image_full`/`image_live`, no TH clip is needed — the cloned-voice narrates over the image.

---

## 4. Prompt design

### 4.1 Image-generation prompt (full / split / live first-frame)
Generate with `nano-banana-2` (accepts `imageUrls`; gpt-image-2 does NOT). Feed the relevant
reference (scene anchor and/or the Candice character ref only if she should appear in the image —
usually she should NOT; the image is of the THING).

Template (photoreal channel still):
```
Photoreal {close-up | overhead | product} image of {LITERAL subject of the sentence},
in {a lived-in home candle workshop / on a rustic wooden bench}, warm natural daylight,
shallow but honest depth, true real-world textures, slightly imperfect amateur look —
NOT glossy stock, not cinematic. {explicit defect/detail the sentence names}.
NO on-screen text, no captions, no watermark, no logos, no hands unless the sentence needs them,
no people unless the sentence is about a person. 16:9.
```
Rules:
- **Literal first.** The subject = exactly the noun the sentence is about, with the exact
  attribute named (a *deep* sinkhole, a *cloudy* wet spot, a *frosted* top).
- **On-aesthetic:** warm workshop, amateur-real, not stock/cinematic (matches the iPhone doctrine).
- **Hard NO-TEXT** (veo/image models love to add captions): forbid all text every time.
- **Comparisons/labels:** if the sentence is "$2 vs $20" or "wet spot vs clean", generate a
  clean two-up composition (two objects side by side); add the label as a POST overlay in the
  assembler (crisp, controlled) rather than trusting the model to render legible text.
- **No accidental Candice:** if she isn't in the image, do NOT pass her ref (avoids a stray face
  that would trip the face gate). If she IS in it, pass her ref and it goes through the face gate.

### 4.2 Motion prompt (come-to-life)
veo `videoInputMode:"keyframes"`, `imageUrls:[the still]` (the still is the first frame), short
motion description:
```
The still photo comes to life with subtle real motion: {flame flickers / steam rises / wax
glistens / dust drifts in the light} and a slow gentle camera {push-in | drift}. Photoreal,
physically correct, nothing morphs or spawns, no people appear, no on-screen text. ~3 seconds of motion.
```
Keep motion SMALL — a living photo, not a new scene. Big motion = morphing/AI tells.

### 4.3 "Input image that comes to life" (user-supplied reference)
When the user provides a real image (a product shot, the e-book cover, a real candle photo):
- Host it on a STABLE raw URL (committed to the repo, served via raw.githubusercontent — temp
  hosts expire mid-run).
- Use it directly as the keyframe (`keyframes` mode) for come-to-life, or as the full-frame still.
- This is the SAME mechanism the book CTA uses; reuse `book_cta_th.py`'s submit path.

---

## 5. Sourcing & specs
- Generate stills at **16:9** for full/live. For split, the image only needs to fill the right
  pane (~690x720) — generate 16:9 and crop, or generate a portrait-ish crop.
- One image model job per image beat; submit in waves of ≤5 (image endpoint has its own ~7
  concurrent cap — back off on FORBIDDEN like the video path).
- Reuse `gen_thumb_generic.py`'s `images/generate` + poll + download flow.

---

## 6. Assembly recipes (ffmpeg)

All segments normalized to 1280x720 / 24fps / AAC 48k, then joined by the smooth assembler
(§ per-boundary crossfades). Per mode:

**A. Full-frame (Ken Burns), narrated by TTS** — `D` = beat dur:
```
ffmpeg -loop 1 -i still.png -i narration.mp3 -filter_complex \
 "[0:v]scale=2560:-1,zoompan=z='min(zoom+0.0006,1.12)':d=D*24:s=1280x720:fps=24,format=yuv420p[v];\
  [1:a]aresample=48000,apad,atrim=0:D,asetpts=PTS-STARTPTS[a]" -map [v] -map [a] -t D ... seg.mp4
```
(zoom direction: `min(zoom+...)` = in; for out start at 1.12 and `max(zoom-...,1.0)`.)

**B. Split-screen** — TH clip `th.mp4` (its own audio) + still `img.png`, TH left 46%:
```
ffmpeg -i th.mp4 -i img.png -filter_complex \
 "[0:v]scale=1280:720,crop=590:720:(in_w-590)/2:0[L];\
  [1:v]scale=2000:-1,zoompan=z='min(zoom+0.0005,1.10)':d=DUR*24:s=690x720:fps=24[R];\
  [L][R]hstack=2,format=yuv420p[v]" -map [v] -map 0:a ... seg.mp4
```
(590+690=1280. Crop the TH centred on her face. Mirror = swap L/R and use th_side.)

**C. Come-to-life**: take the veo img2video clip, trim to D, narrated by TTS (mux TTS over the
muted veo clip exactly like a B-roll gap segment).

**Audio routing:** `image_full` & `image_live` pull from the consolidated cloned-voice gap TTS
(extend the existing gap mechanism so an image beat is just another narrated gap with a visual);
`image_split` keeps the TH clip's veo audio.

---

## 7. Quality gates (extend the existing gates)
Run on image segments too:
- **Literal-match:** a vision check that the image actually shows the sentence's subject.
- **NO-TEXT:** OCR/vision check the still and the live clip for accidental captions/watermark
  (use vision, not raw tesseract — it misses low-contrast text).
- **Face gate:** only if Candice is supposed to be in the image (split keeps the normal TH face
  gate on the TH pane). A stray generated face in a "thing" image = regenerate.
- **Watermark:** come-to-life clips are veo output → delogo the bottom-right like all veo clips.
- **Truncation:** image beats narrated by TTS are NOT 8s-capped (TTS has no limit), so no
  truncation risk — but keep image-beat sentences short for pacing.

---

## 8. Implementation hooks (for the build)
- `buildkit.py`: add `img_full(sentence, image_prompt, **kb)`, `img_split(sentence, image_prompt, th_side)`,
  `img_live(sentence, image_prompt, motion)` helpers that append `type:"image"` beats with the
  schema in §3; the chain/scene logic ignores image beats (they're standalone visual beats).
- A `gen_images.py` (mirror of `gen_thumb_generic.py`): generate every image beat's still via
  nano-banana-2, host stable, store path in state.
- For `image_live`: reuse the `book_cta_th.py` keyframes submit to animate the still.
- Assembler (`assemble_smooth.py`): add per-`visual_mode` segment builders (§6) before the
  crossfade join; image_split also consumes the beat's TH clip.
- Scheduler: at script-build time, tag each body beat's `visual_mode` per §2 and enforce the
  rhythm guardrails, targeting the §0 mix.

---

## 9. One-paragraph summary for the writer
Write the script as before, then for each body sentence decide: is this a face moment (talking
head), a "look at this" moment (full-frame image), an "explain-while-showing" moment (split),
a hero/beauty moment (come-to-life), or a physical action (hands B-roll)? Aim for ~35% face and
the rest carried by images/B-roll, changing the visual every 3-6s. Every image is LITERALLY of
what she's saying, on the warm amateur workshop aesthetic, text-free, Ken-Burns'd so it breathes;
come-to-life clips animate a still subtly; split keeps her cropped beside the image. Her cloned
voice narrates the image beats; her veo voice carries split and full talking-head beats.
