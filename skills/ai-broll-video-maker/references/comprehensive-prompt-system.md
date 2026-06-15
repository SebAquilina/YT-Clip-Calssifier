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
