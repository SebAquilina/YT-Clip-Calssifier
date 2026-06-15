# The iPhone B-roll doctrine (Elias-Yoder style)

This is the heart of the skill. Every body shot is a **Mode B** (no character on
screen) Veo 3.1 Lite clip, and every one of them must obey the doctrine below.
The Veo mechanics are in `veo-prompting.md`; this file is about the *look and the
match* that make the footage read as Elias Yoder rather than generic AI B-roll.

## Why iPhone, not cinematic

The niche (Amish / old-ways / lost-knowledge self-sufficiency) sells **trust**.
The viewer believes a real off-grid person, or someone documenting them, walked
through a real farmhouse and filmed the actual thing. The cues that signal "real
person, real place, right now" are the cues of phone footage: everything in
focus, a slightly wide lens, natural light, a touch of handheld wobble, true
color. The cues that BREAK it are the cues of professional production: creamy
background blur (bokeh), film grain, a teal-and-orange grade, glassy gimbal
moves, perfect framing. **In this niche, "lower production value" reads as higher
trust.** That is the entire reason this skill exists instead of the cinematic
default — do not "improve" the footage into looking produced.

## The iPhone token block — paste into EVERY B prompt, verbatim

Append this style clause to every beat prompt (it replaces the parent skill's
"shot on 35 mm, shallow depth of field, subtle film grain" tags):

> shot on a modern smartphone, deep focus with everything sharp front to back,
> wide ~26 mm-equivalent lens, natural available light, slight handheld
> micro-shake, true-to-life color, crisp fine detail, no bokeh, no film grain,
> no cinematic color grade

Notes on why each token earns its place:
- **deep focus / everything sharp** — kills the AI instinct to throw a creamy
  bokeh background; phones have tiny sensors and hold deep focus.
- **wide ~26 mm-equivalent** — the native iPhone main-camera field of view; it
  reads instantly as "phone" and slightly distorts close foreground the way a
  phone does.
- **slight handheld micro-shake** — the single most important "real person"
  token. Perfectly locked footage reads as a tripod/AI. Keep it *slight* — not
  shaky-cam.
- **true-to-life color, no grade** — phone footage is a little flat and accurate,
  not stylized. A graded look is a tell.
- **no bokeh, no film grain** — the two most common AI-cinematic tells; name them
  out as negatives even though Veo handles negation poorly, because in practice
  `no bokeh, no film grain` in the style clause reduces them.

## The two shot tiers (the "majority iPhone" knob)

The user wants the **majority** of clips to look phone-shot. Use two tiers and
keep the default dominant:

- **Tier 1 — handheld walk-through (DEFAULT, ~80% of clips).** Add: *handheld,
  the operator is holding the phone and moving slightly, a small natural sway,
  as if filming while crouching to look closer.* Pair with close/medium framing.
  This is the texture of the channel.
- **Tier 2 — propped phone (hero/establishing, ~20%).** Add: *the phone is
  propped on a surface, mostly still with a tiny residual drift.* Use for a clean
  establishing shot of a location (the farmhouse from the yard, the full attic) —
  steadier, but STILL a phone (deep focus, wide lens, natural light). Never make
  this a cinematic crane/dolly — steadier ≠ produced.

Pick the tier per beat in Stage B2; bias Tier 1. A run that is mostly Tier 2
looks like a real-estate listing, not Elias Yoder.

## The literal-match rule (the other half of the doctrine)

The look only works if the shot is OF the sentence. Procedure per beat:
1. Quote the verbatim sentence at the top of the prompt (a note to yourself).
2. Extract the ONE concrete noun + its state/action the viewer's eye lands on.
3. Build the entire shot around depicting THAT, literally and specifically.

Match, don't theme:
- "a four-dollar strip of cotton muslin nailed under the rafters" → weathered
  hands tacking a pale muslin strip flat against bare attic rafters, a few nails
  held in the other hand. NOT "a cozy attic", NOT "an old house interior".
- "the cupola on the roof lets the hot air climb out" → a small wooden roof
  cupola seen from below against sky, faint heat shimmer at its louvers. NOT "a
  farmhouse roof".
- "a root cellar that holds a steady fifty-four degrees" → a dim earthen cellar,
  shelves of jars and crates, cool damp stone walls, a thermometer on a post.
  NOT "a basement".

If a sentence has no concrete image (a pure argument or feeling), it is a
**talking-head candidate**, not a B-roll beat — do not force a literal-but-random
shot onto it. Hand it back to Stage B1/Stage 4. Usually the adjacent concrete
sentence carries the visual.

## Hands-at-work are HERO shots (a deliberate departure)

The parent skill bans disembodied hands as an artifact. **Reverse that here.**
Elias-style authenticity lives in close shots of plain, weathered hands doing the
actual practical task — and those are the most convincing "a real person made
this" frames in the whole video. Engineer them, don't avoid them:

- Add a **consistent hands tag** to every hands beat (part of the continuity
  bible): *a man's weathered, work-worn hands, plain rolled-up sleeves of a
  homespun shirt, no rings, no watch.* This keeps the hands the same person
  across the video and keeps them period-accurate.
- Keep the action a **single slow arc**: tacking a strip, prying a vent slat,
  turning a valve, setting a jar on a shelf, striking a match to a lamp. Veo
  handles one slow gesture well; it mangles fast fine-finger work (knot-tying,
  threading a needle) — keep those off-screen or implied.
- Frame close/medium, Tier 1 handheld, deep focus. The slight wobble + close
  hands + a real task = the channel's signature shot.

## The B-prompt skeleton (assemble from veo-prompting.md's 7 components)

```
# beat sentence: "<verbatim sentence>"
[Tier-1 handheld | Tier-2 propped] [shot type: close-up / medium / wide
establishing], [slow camera move if any]. <The ONE hero noun, with 2–3 concrete
physical details>, <single slow action arc>, in <the continuity-bible location
with its background elements>. <Continuity-bible light: named source + quality>.
<iPhone token block, verbatim>. SFX: <2+ specific diegetic sounds>. Ambient
noise: <explicit room/outdoor tone> (no music). (no subtitles)
<continuity bible block, verbatim>
```

Length 80–130 words (same rigor as any Veo prompt — "B-roll" never means
"brief"). No person, no dialogue (narration runs over it). If the action implies
hands and hands are wanted, use the hands tag; otherwise recompose around the
object so no stray limbs appear.

## Worked examples

**Tier 1 — hands at work (the signature shot):**
```
# beat sentence: "He nailed a four-dollar strip of cotton muslin under the rafters."
Handheld close-up, a small natural sway as if the operator is crouching in low
light to film. A man's weathered, work-worn hands press a pale strip of cotton
muslin flat against rough, bare attic rafters and tap a nail through it with a
small hammer, one slow tack. Dust drifts in a shaft of daylight from a gable end.
Shot on a modern smartphone, deep focus with everything sharp front to back, wide
~26 mm-equivalent lens, natural available light, slight handheld micro-shake,
true-to-life color, crisp fine detail, no bokeh, no film grain, no cinematic
color grade. SFX: a single hammer tap, the creak of an old joist. Ambient noise:
still, warm attic air, faint birdsong outside (no music). (no subtitles)
[CONTINUITY BIBLE: 1934 timber farmhouse attic, bare hand-hewn rafters, warm pine
tones, hot still summer afternoon, daylight from a gable vent at frame left;
a man's weathered hands, plain rolled homespun sleeves, no rings or watch.]
```

**Tier 2 — propped establishing shot:**
```
# beat sentence: "The upstairs bedroom of the farmhouse my grandfather built in 1934 stays cool in August."
Propped phone, mostly still with a tiny residual drift, wide establishing shot. A
plain timber-framed farmhouse with a small roof cupola sits in a green Pennsylvania
field under a hazy August sky, a clothesline and a hand-water pump in the yard, no
power lines anywhere. Shot on a modern smartphone, deep focus with everything sharp
front to back, wide ~26 mm-equivalent lens, natural available light, slight
handheld micro-shake, true-to-life color, crisp fine detail, no bokeh, no film
grain, no cinematic color grade. SFX: cicadas, a distant rooster. Ambient noise:
open warm farmland air, a soft breeze (no music). (no subtitles)
[CONTINUITY BIBLE: same 1934 timber farmhouse, weathered grey siding, green field,
hazy hot August light, warm natural color.]
```

**Tier 1 — object detail (the gable vent):**
```
# beat sentence: "The gable vents your contractor probably sealed shut."
Handheld medium close-up, a small sway, tilting slightly up. A wooden louvered
gable vent set into weathered farmhouse siding, paint flaking, one slat hanging
loose so a sliver of dark attic shows behind it. Warm late-afternoon light rakes
across the boards. Shot on a modern smartphone, deep focus with everything sharp
front to back, wide ~26 mm-equivalent lens, natural available light, slight
handheld micro-shake, true-to-life color, crisp fine detail, no bokeh, no film
grain, no cinematic color grade. SFX: a faint whistle of moving air, a board
creak. Ambient noise: quiet outdoor farmstead, insects (no music). (no subtitles)
[CONTINUITY BIBLE: same 1934 farmhouse, weathered grey siding, hazy hot August
light, warm natural color.]
```

## Failure modes specific to this style

| Symptom | Cause | Fix |
|---|---|---|
| Footage looks "produced" / cinematic | iPhone block dropped or weak | Re-pin the full token block; add "no bokeh, no film grain, no cinematic color grade" |
| Creamy blurred background | Veo defaulted to shallow DOF | Add "deep focus everything sharp front to back" + "wide 26 mm" |
| Shot is near the topic but not OF the sentence | Themed instead of literal | Re-extract the one hero noun+action; rebuild the shot around it |
| Every clip a different farmhouse/attic | No bible / no anchor keyframe | Pin the bible verbatim; attach the location anchor frame as keyframe |
| Hands look fake / fast finger work | Action too fine for Veo | One slow arc only; keep fine work off-screen; hands tag for consistency |
| Anachronism (wires, switch, car) | Period gate skipped | Run the period-authenticity panel on the prompt; regenerate |
| Locked, tripod-still feel | No handheld token | Add "slight handheld micro-shake" (Tier 1) — the key realism cue |
