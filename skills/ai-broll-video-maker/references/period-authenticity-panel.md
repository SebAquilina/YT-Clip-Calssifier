# Period-authenticity panel (the niche reality gate)

Run this on **every B-prompt before it is queued**, and on **sampled frames after
generation** (Stage B5). In the Amish / old-ways niche, a wrong-period object is
as fatal as a glitched hand — both instantly tell the viewer "this is fake" and
destroy the trust the whole channel runs on. This is the parent skill's
reality-panel idea, re-pointed from "can Veo do this motion" to "is this shot
period-true and tell-free".

## Run it as a quick 3-lens check (inline is fine — no subagents required)

For each prompt, read it through three lenses and rewrite until all pass:

### Lens 1 — Anachronism auditor (period truth)

Nothing modern may appear or be implied. Reject and rewrite if the prompt
contains, implies a background with, or invites Veo to add any of:

- **Power**: power lines, utility poles, electrical wires, light switches,
  wall outlets, electric bulbs, lamps with cords, breaker boxes, solar panels.
  (Light is daylight, oil/kerosene lamp, lantern, candle, or stove-fire only.)
- **Machines/tech**: cars, trucks, tractors with cabs, phones, screens, clocks
  with digital faces, modern HVAC units, plastic anything, vinyl, PVC pipe,
  power tools, refrigerators, microwaves.
- **Dress tells** (if any clothing is in frame, e.g. the hands' sleeves): visible
  zippers, plastic buttons, branded logos, wristwatches, rings, sneakers,
  synthetic fabric sheen. Plain homespun, suspenders, bonnets, broadfall trousers,
  boots only.
- **Materials that read modern**: chrome, stainless steel appliances, laminate,
  particleboard, bright printed packaging, barcodes.

Positive replacements (describe what you DO want, per Veo's "describe don't
instruct" rule): hand-hewn timber, cast iron, tin, crockery, glass mason jars,
oiled wood, wrought-iron hardware, woven baskets, muslin/cotton/wool, clay,
fieldstone, daylight and lamplight.

Add to the prompt's NEGATIVE list (noun list, no sentences):
`power lines, electrical wires, light switch, outlet, car, phone, screen,
plastic, zipper, wristwatch, modern appliance, logo, text overlay, subtitles,
watermark`.

### Lens 2 — AI-tell auditor (generation truth)

Reject/rewrite shots that invite the classic Veo failures:
- **Hands**: fast fine-finger work (knot-tying, threading, counting coins) →
  morphs fingers. Keep one slow gross-motor arc; put fine work off-screen.
- **Text on objects**: tool brands, jar labels, signage, book pages in focus →
  Veo writes gibberish. Keep text out of focus or out of frame.
- **State changes**: pouring liquid, breaking, shattering, fire spreading, water
  filling → physics glitches. Imply before/after instead of the transformation,
  or keep the change small and slow (a single match flame, steam rising).
- **Crowds / multiple people** → identity drift and extra limbs. B-roll is
  objects and at most one set of hands.
- **Reflections / mirrors** → render the AI scene incorrectly; avoid.

### Lens 3 — Authenticity editor (does it sell "a real person filmed this")

Even period-true and tell-free, a shot can still feel staged. Push for the phone-
documentary texture:
- Is it Tier 1 handheld with the micro-shake token? (Locked = fake.)
- Is the framing slightly imperfect, the way a person crouching to film would
  get it — not a perfectly centered hero composition?
- Is the light the bible's natural source, not a studio key?
- Would a real off-grid person actually point a phone at THIS, right now, while
  explaining it? If the shot is too pretty/composed to be candid, rough it up.

## Frame-scan after generation (Stage B5)

Pull the middle frame of each sampled clip and scan for any Lens-1 anachronism or
Lens-2 tell. A single hit fails the clip → regenerate with a tightened prompt and
the negative list re-pinned. Sample the first half densely (highest-retention),
and any clip in a recurring location at least once for continuity drift.

## One-pass checklist (use per prompt)

```
[ ] No power/tech/dress/material anachronism in or implied by the prompt
[ ] Negative noun-list appended
[ ] No fast finger work, in-focus text, pour/break/fill, crowd, or mirror
[ ] Tier 1 handheld + micro-shake (or justified Tier 2)
[ ] Light = the bible's natural source
[ ] Framing candid, not a centered hero composition
[ ] Continuity bible pasted verbatim; anchor_keyframe set if location ≥3 beats
```
