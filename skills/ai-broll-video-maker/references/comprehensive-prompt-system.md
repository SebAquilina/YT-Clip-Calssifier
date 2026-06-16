# Comprehensive prompt system (consistency + realism)

Field-proven on the Candice candle channel after two failure modes appeared:
faces drifting between clips, and physically-impossible actions (liquid poured
into nothing, wicks "cut" without the scissors touching them). Both are prompting
problems — the model can render these correctly when the prompt is explicit.

## The rule: every prompt is five blocks, always in this order

```
ACTION  +  CAMERA  +  PERSON-CONSISTENCY  +  WORLD(bible verbatim)  +  REALISM/NEGATIVE
```

1. **ACTION** — one concrete subject doing one concrete, physically-complete
   action. Name **every** object involved and its state. For a pour, name BOTH
   vessels and the path: *"a thin stream of warm cream wax pours from a stainless
   steel pitcher INTO a clear glass jar on the table, filling it level."* For a
   cut, the tool must contact the thing: *"small scissors close on a single
   upright cotton wick and snip the charred tip clean off, the wick still
   standing."* Vague actions are where the model invents impossible physics.

2. **CAMERA (iPhone block, verbatim)** — *Filmed casually on a modern smartphone
   held in one hand: wide ~26mm lens, deep focus with the whole frame sharp,
   natural window daylight, slight handheld micro-shake, true-to-life color and
   realistic fine detail; no bokeh, no shallow depth of field, no film grain, no
   cinematic grade.*

3. **PERSON-CONSISTENCY (verbatim, every clip)** — *Whenever a person appears she
   is the exact same woman as in the reference image: <fixed physical description>;
   identical face, hair and clothing in every shot.* Paired with **attaching the
   reference image to every job** (see below) this is what stops the face drifting.

4. **WORLD** — the continuity bible, pasted verbatim and unchanged into every clip.

5. **REALISM / NEGATIVE** — *Photo-real and physically correct: every object is
   solid, whole and clearly present; liquids pour from a real visible container
   into another real visible container; hands have exactly five natural fingers
   and hold objects correctly; tools actually contact what they act on. NEGATIVE —
   do not show: floating or disappearing objects, liquid from nothing or poured
   into empty air, bending/morphing tools, extra or fused fingers, warped or
   melting faces, duplicated people, glowing outlines or rim-light around the
   person, and no text, captions, watermarks, logos or gibberish labels.*

## Reference image on EVERY clip (the face-consistency fix)

Attach the locked reference photo to **every** job, not just talking heads:

- **Talking heads / any shot that features her** → `videoInputMode: "keyframes"`
  (reference is the first frame → her face is locked exactly).
- **B-roll (hands / objects)** → `videoInputMode: "ingredients"` (reference is a
  style/character anchor → same woman and same room whenever she is visible,
  without forcing her into a hands-only shot).

Host the reference somewhere stable. Anonymous temp hosts (litterbox/catbox)
expire or rate-limit mid-run and every clip then fails with *"URL is not valid"*;
a committed file served from `raw.githubusercontent.com` on a public repo is
stable and free.

## "Come-to-life" hook without outlines/floating graphics

Generate the hook as a normal **muted keyframe video** from a clean photographic
base (or the reference), prompting only small natural motion (breathing, a glance,
a flickering flame). Put the negative block to work: *no glowing outline or
rim-light around the person, no floating objects, no text/arrows/checkmarks/
graphics.* Never animate the finished thumbnail (its title text and sticker
graphics animate into floating garbage).

## Talking heads speak for themselves (do NOT voice them over)

A talking-head/character clip must use **its own in-clip Veo speech**. At that
moment the narrator voiceover **goes silent** — you do not lay the narration over
a talking head, and you never time-stretch the clip to a narration track (that is
exactly what throws the lips out of sync). Assembly rule (see
`scripts/assemble_segmented_v2.py`): character beats are muxed with their own
native audio at their own rate; only B-roll beats carry the narrator VO.

Match the talking head's spoken accent to the channel's narrator voice (e.g. an
American narrator → prompt the talking head to "speak in a warm, natural American
accent"), so the two voices feel like one person rather than a presenter plus a
separate voiceover. To change a talking head's voice you must regenerate that
clip — its speech is baked into the video; never dub it.

## Reinforced physics & continuity rules (scene-dependent)

AI clips break on small physical impossibilities. Enforce a GLOBAL block on every
prompt, plus a SCENE block chosen by the beat's action type.

### GLOBAL (every clip, both Veo and Grok)
- **Object permanence:** everything visible in the first frame stays present and
  consistent the whole clip; nothing pops into existence and nothing vanishes;
  items on the shelves stay put.
- **Wardrobe is already on:** the person is fully dressed (sweater + apron) from
  frame one; clothing never appears, snaps on, or changes mid-shot.
- **Hands:** five fingers, natural grip; a tool is held correctly and actually
  touches what it acts on; no teleporting objects into the hand.
- **Text:** avoid readable text. Prefer unlabeled jars or plain kraft labels with
  NO legible words; if a label must read, one short real word in clean print only
  — never sentences (AI garbles them). Negative: no gibberish/warped letters.

### SCENE blocks (inject the one matching the action)
- **POUR:** the destination jar is OPEN and lidless; a continuous stream leaves
  the spout and lands INSIDE the open jar; the level rises. Negative: no lid/cap
  on the jar, no liquid passing through a closed top, no pouring into empty air.
- **WICK TRIM / CUT:** a single wick is clearly present and upright; the blades
  close ON the wick and cut at the wick tip; the cut piece falls; the wick stays
  rooted. Negative: no cutting empty air or the wax, no missing wick.
- **CENTER WICK (peg / clothespin / wick bar):** an actual wick is present; the
  peg straddles and pinches THAT wick across the jar rim, the wick visible between
  its jaws, held centered. Negative: no peg clamping nothing, no absent wick.
- **HEAT GUN / SMOOTH FINISH / FIX SINKHOLE:** the heat gun points at the wax
  surface from a few inches; the top visibly melts smooth and level; tool is real
  and present the whole time. Negative: no floating heat gun, no instant change.
- **SECURE TOPPINGS / BOTANICALS:** dried botanicals rest on the wax and are
  gently pressed/melted in; they stay embedded. Negative: nothing floats or
  vanishes; toppings don't multiply.
- **PLACE / SET / WASH:** the hand moves the object into place continuously; it is
  never teleported; water/soap behaves normally.

To change a talking head's voice you regenerate the clip; physics issues are
fixed by adding the matching SCENE block, not by re-rolling blindly.

## Grok video prompting (xAI Grok Imagine) — how it differs from Veo
Research-backed (xAI/Replicate/community guides). Grok prefers **natural-language
scene description, not keyword piles**, and a tight motion focus:
- Structure: **Subject + Action + Setting + Camera movement + Motion detail +
  Lighting/Mood**, written as 2–4 plain sentences.
- **Name the camera move** explicitly ("slow push-in", "static close", "handheld
  follow") — these map directly to the animation.
- **1–2 clear actions** per clip; keep it short for motion stability (don't pack
  five beats into one clip).
- **Image-to-video:** focus on the added MOTION + camera, not on re-describing the
  scene (the input image already gives context).
- State physics as plain descriptive clauses ("the jar stays open with no lid; the
  hand has five fingers") rather than a separate NEGATIVE list — Grok follows
  natural language better than tag-style negatives.
- 69labs note: `grok-imagine-video` costs **3 credits/clip** (vs 1 for veo-video),
  `maxImageUrls` = 1, modes normal|spicy|fun (use normal). Wave-schedule to the
  100/hr cap (~33 Grok clips/hour).
