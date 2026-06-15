# Veo 3.1 / 3.1 Fast prompting guide

Distilled from Google's official documentation (Gemini API Veo docs, the
Vertex AI prompt guide & best-practices pages, the Google Cloud "Ultimate
prompting guide for Veo 3.1", and the Veo 3.1 developers-blog launch post),
with community findings only where Google is silent. Veo 3.1 **Fast** takes
the *same prompts* as standard 3.1 — it differs only in latency and price —
so everything here applies unchanged.

Sources: ai.google.dev/gemini-api/docs/video ·
docs.cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide ·
docs.cloud.google.com/vertex-ai/generative-ai/docs/video/best-practice ·
cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1 ·
developers.googleblog.com/introducing-veo-3-1-and-new-creative-capabilities-in-the-gemini-api

## 1. The prompt formula

Google's five-part structure, plus audio:

> **[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance] + [Audio]**

- **Cinematography** — shot type, camera angle, camera movement, lens.
- **Subject** — the person/object/animal that is the focus.
- **Action** — what the subject is doing. One action arc per clip.
- **Context** — the environment: where, when, what's in the background.
- **Style & Ambiance** — lighting, mood, color palette, artistic style.
- **Audio** — dialogue, SFX, ambient noise, music. Veo 3.1 ALWAYS generates
  audio; if you don't specify it, Veo invents it.

Not every element is mandatory, but for a near-100% hit rate specify all six.
Write clear, direct, specific prose — no "kind of", no vagueness. Adjectives
and adverbs paint the picture. For faces, Google's tip: use the word
"portrait" / ask for facial detail as a focus.

**One scene per prompt.** Google's best-practices page is explicit: focus
short videos on a single scene. "A then B then C" in one clip produces
muddled output. For deliberate multi-shot clips, use timestamp prompting:

```
[00:00-00:03] Medium shot, the kettle starts to rattle on the stove.
[00:03-00:08] Close-up: steam bursts from the spout. SFX: a rising whistle.
```

## 2. Dialogue and audio syntax

**Dialogue — the colon rule (Google's documented anti-subtitle guidance):**
use a colon after the speaker's action and **no quotation marks**.

- Recommended: `The woman says: My name is Clara.`
- Not recommended: `The woman says: "My name is Clara."` — quotation marks
  make Veo render text on screen.

Always specify the voice and delivery — it shapes both the audio and the lip/
face animation: `In a voice that is crisp and clear, with a thoughtful,
analytical tone and a standard American accent, Clara says: It has to be here`.

**Dialogue length:** ~15–25 words fits an 8-second clip naturally. Longer
lines get rushed and break lip sync; very short lines invite Veo to fill the
silence with invented gibberish speech. One or two exchanges max per clip.

**Multiple speakers:** tag lines to visually distinct descriptions —
`The woman wearing pink says: … The man with the glasses replies: …` —
otherwise the wrong mouth moves.

**Mispronunciations:** spell hard names phonetically in the line.

**SFX:** describe explicitly, or use the `SFX:` prefix —
`SFX: thunder cracks in the distance`, `tires screeching loudly`.

**Ambient noise:** always include a sentence —
`Ambient noise: the quiet hum of a starship bridge`. Unspecified ambience is
how phantom studio-audience laughter and random music sneak in. If you want
no music, say so descriptively: `(no music)`.

**Music:** describe genre/mood in prose —
`upbeat electronic music with a rhythmical beat is playing` — or Veo chooses.

**Avoiding burned-in subtitles (known Veo failure mode), in order:**
1. Colon syntax, no quotation marks (above).
2. Append `(no subtitles)` after the dialogue sentence — a tolerated
   exception to the no-negation rule that works well in practice.
3. Negative-prompt list: `subtitles, captions, text overlay, on-screen text,
   watermark`.
4. Avoid contractions in dialogue; don't place dialogue in the final second.

## 3. Character consistency & talking heads

**Reference image (Veo 3.1 "ingredients"):** supplying the character's photo
is the strongest consistency tool — Veo preserves the subject's appearance.
Rules when a reference is attached:

- **Prompt for motion only.** Do not re-describe the face, hair, or clothing
  already visible in the reference — redundant description fights the image
  and causes drift. Refer to the character generically: "the woman", "she",
  "the subject".
- Reference photos work best clean: plain background, well lit, front-facing.
- 8-second duration is the safe choice with reference images (it is the
  required duration on Google's own API when references are used).

**Text-only fallback** (no reference available): write a detailed character
sheet — age, build, hair color/style, facial structure, eye color, defining
marks, AND a voice description — and paste it **verbatim, unchanged** into
every scene's prompt, changing only action/setting. Reuse the same seed if
the platform exposes one.

**Lip sync** is native — no special syntax beyond the dialogue rules. The
generated voice's pacing drives the mouth animation; since the revoice stage
preserves the original lip timing, the dialogue text fed to Veo must be the
final script line.

## 4. Cinematography vocabulary Veo reliably understands

- **Composition / angles:** extreme close-up, close-up, medium shot (the
  dialogue workhorse), full shot, wide shot / establishing shot,
  over-the-shoulder, two-shot, eye-level, low-angle, high-angle, bird's-eye /
  top-down, worm's-eye, Dutch angle, POV shot.
- **Movement:** static shot, pan left/right, tilt up/down, dolly in/out,
  truck, pedestal, zoom in/out, tracking shot, crane shot, aerial/drone,
  handheld/shaky cam, whip pan, arc shot, slow pan.
- **Lens & focus:** wide-angle, telephoto, macro, fisheye, shallow depth of
  field (bokeh), deep focus, soft focus, rack focus, lens flare, dolly zoom.
- **Lighting:** soft morning sunlight through a window, golden hour glow,
  moonlight, flickering candlelight, harsh fluorescent office lighting,
  pulsating neon, Rembrandt lighting, film noir deep shadows, high-key,
  low-key, volumetric light, backlit silhouette.
- **Style:** photorealistic, cinematic, "shot on 35mm film", anamorphic
  widescreen, film grain, 8K, Japanese anime style, Pixar-like 3D, claymation,
  stop-motion, watercolor, gritty graphic-novel illustration.
- **Temporal:** slow-motion, time-lapse, fast-paced action, rhythmic movement.

A touch of film texture ("subtle film grain, shot on a mirrorless camera")
counters the too-clean AI look.

## 5. Negative prompting

Google's rule: **describe, don't instruct.** Inside the prompt body, never
"no X" / "don't show X" — Veo handles negation words poorly. Instead:

- Describe the desired absence positively: "a desolate landscape with no
  visible buildings" → better: "a desolate, empty landscape of bare rock".
- If the platform exposes a negative-prompt field, give it a comma-separated
  **noun list** (not sentences): `subtitles, captions, text overlay,
  watermark, extra people, distorted hands`.
- Exception that works in practice: `(no subtitles)` and `(no music)`
  parentheticals after the audio sentences.

## 6. Veo 3.1 Fast facts

- Durations 4 / 6 / 8 s (8 s required for reference-image generation and
  high-res output on Google's API — default to 8).
- Aspect 16:9 or 9:16; 720p/1080p (4K on 8s clips where offered); 24 fps.
- **Audio is always on** — cannot be disabled, so always script it.
- Safety filters sometimes block generation *because of the audio* — if a
  generation is rejected, rephrase the dialogue before assuming the visual
  is the problem.
- Veo is unusually deterministic: identical prompt ≈ similar output. To get
  a different take, change the prompt, not just the retry button.

## 7. Failure modes → prompt-arounds

| Failure | Prompt-around |
|---|---|
| Burned-in garbled subtitles | Colon dialogue, no quotes; `(no subtitles)`; negative list; no contractions |
| Rushed / gibberish speech | 15–25 words per 8s; never leave a speaking character with nothing scripted |
| Wrong speaker talks | Tag lines to distinct visual descriptions |
| Phantom laughter / wrong music | Always script ambience explicitly; `(no music)` if none wanted |
| Character drift across clips | Reference photo + generic in-prompt references ("the woman"); never re-describe her |
| Disembodied / morphed hands | Recompose around the object as hero; avoid complex hand–object interaction; simple single actions |
| Muddled multi-event clip | One moment per clip; split scenes; or explicit timestamp prompting |
| Generic "AI look" | Concrete craft terms + film-texture descriptors |
| Generation blocked | Often the audio — rephrase dialogue, retry |

## 8. Worked examples

**Mode A — talking head (character reference attached):**

```
A medium shot, camera static, eye-level. The woman sits at a warmly lit
kitchen table, late-afternoon sun through a window behind her, a mug of tea
by her hand. She leans in slightly and raises one finger, her expression
kind but firm. In a warm, unhurried voice with a gentle reassuring tone, she
says: Before you pay anyone to fix that boiler, try this one valve first
(no subtitles). Ambient noise: quiet kitchen room tone, a soft clock tick
(no music). Photorealistic, shot on a mirrorless camera, shallow depth of
field, subtle film grain.
```

**Mode B — no character (no reference):**

```
Slow dolly in, close-up. An old brass radiator valve, flecked with paint,
slowly turning as steam begins to rise around it in a dim utility room.
Cold blue window light from the left, warm glow from a bare bulb above.
Photorealistic, moody, shallow depth of field, subtle film grain.
SFX: a metallic creak, then a low hiss of steam. Ambient noise: muffled
pipework hum (no music).
```

**Google's own Clara example (character + voice consistency, colon dialogue):**

> "A medium shot, with the camera slowly dollying forward in a dimly lit,
> grand Parisian archive. Dust motes dance in a single beam of light from a
> high window. Clara, a historian in her early 30s, with observant, dark
> brown eyes… dressed in a sophisticated, dark navy-blue wool coat… She
> stands before a large, ancient wooden table, carefully turning the fragile,
> yellowed page of a massive, leather-bound book. Her expression is one of
> deep concentration. In a voice that is crisp and clear, with a thoughtful,
> analytical tone and a standard American accent, Clara says: It has to be
> here"

**Google's two-speaker example:**

> "A medium shot in a dimly lit interrogation room. The seasoned detective
> says: Your story has holes. The nervous informant, sweating under a single
> bare bulb, replies: I'm telling you everything I know. The only other
> sounds are the slow, rhythmic ticking of a wall clock and the faint sound
> of rain against the window"
