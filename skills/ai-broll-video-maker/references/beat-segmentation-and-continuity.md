# Beat segmentation + continuity engine

Two jobs: (1) cut each body segment's narration into 6–9 s **visual beats**, one
clip per beat; (2) keep the world continuous across the dozens of separately-
generated clips so they read as one place.

## Part 1 — beat segmentation

The unit of the whole engine is the **beat**: the smallest run of narration that
has ONE concrete thing to show. One beat → one prompt → one clip.

### How to cut

`scripts/segment_beats.py` does the deterministic part:
1. Force-align the segment's narration MP3 with faster-whisper to get per-word
   timings (the same `base.en` model the revoice/VM3 stages use).
2. Group words into beats at **sentence and strong-clause boundaries**, targeting
   **6–9 s** per beat (never cut mid-phrase; a comma-clause boundary is fine, a
   mid-noun-phrase cut is not).
3. Emit `beats_<n>.json`: each beat has `id`, `start`, `end`, `dur`, and the
   **verbatim sentence/clause text** it spans.

### The one-visual rule (apply after the automatic cut)

The auto-cut is timing-based; then YOU enforce *one visual per beat*:
- **Two visuals in one beat** ("the cupola on the roof, the muslin under the
  rafters") → split into two beats so each gets its own literal clip, even if that
  makes one beat ~4 s (trim the clip to fit).
- **An abstract sentence with no image** ("none of this is a secret, it's been
  written down for two hundred years") → mark it `abstract`. It is NOT a B-roll
  beat. Either it sits under the *previous* concrete clip held a beat longer, or
  it is a talking-head candidate handed back to Stage 4. Never force a literal
  shot onto an abstraction — that is exactly the "random B-roll" failure.
- **A long list sentence** → one clip per listed item, in order, so the visuals
  track the narration item by item.

### Timing math (volume + waves)

- ~1 clip per 6–9 s of finished video. A 10-minute video ≈ **70–100 beats**.
- Each Veo clip is fixed 8 s; you TRIM down to a shorter beat or SPLIT a longer
  one (Stage B4). Plan the 5-wide waves and a scheduled hourly drain around the
  beat count and the account's real per-hour quota.

## Part 2 — continuity (the "same place" problem)

Eighty independent generations of "the attic" will be eighty different attics.
Three mechanisms, cheapest first. Always do the bible; add anchors as the beat
count in a location grows.

### Mechanism 1 — the continuity bible (text anchor, ALWAYS)

Before generating, write ONE canonical world block for the video and store it in
`manifest.broll.continuity_bible`. It fixes everything that must not drift:

- **The hero structure**: "1934 timber-framed farmhouse, weathered grey siding,
  small roof cupola."
- **Each recurring location**: attic (bare hand-hewn rafters, warm pine tones),
  summer kitchen (cast-iron stove, plank table), root cellar (earthen walls,
  jar shelves), barn, yard.
- **Season + time + light**: "hot still August afternoon, warm natural daylight,
  light rakes from frame left."
- **Color palette**: "warm, slightly desaturated, true-to-life."
- **The recurring person's hands/clothing** (for hands beats): "a man's
  weathered, work-worn hands, plain rolled homespun sleeves, no rings, no watch."

Paste the bible **verbatim, unchanged** at the end of every beat prompt. Only the
shot type and the hero noun/action vary between prompts. This single discipline
removes most drift at zero extra generation cost.

### Mechanism 2 — anchor keyframes (image anchor, for any location ≥3 beats)

A text bible keeps the *kind* of place stable; an anchor keyframe keeps the
*exact* place stable.

1. For each recurring location, generate ONE clean establishing shot first
   (Tier 2 propped, the bible's description of that location).
2. Capture a sharp middle frame from it → `broll/anchor_<location>.jpg`. Store it
   in `manifest.broll.anchor_keyframes`.
3. For every later beat in that location, set the beat's `anchor_keyframe` to that
   location. `batch_generate.py` attaches the frame as the **first-frame keyframe**
   (headless, `references/69labs-video-workflow.md` Recipe 1) before submitting,
   so Veo starts from the real attic and only adds the new action. Rafters, wood
   tone, and light direction now match across all attic beats.

Keep the anchor frame clean (no hands, no transient props) so it generalizes
across many actions in that location. Crop it to 16:9 before attaching (Recipe 0)
or the output pillarboxes.

### Mechanism 3 — last-frame → first-frame chaining (motion anchor, sparingly)

When two adjacent beats should read as ONE continuous moving shot (a slow push in
toward the gable vent, a walk across the yard), set the second beat's `chain_from`
to the first beat's id. The client captures the first clip's LAST frame and feeds
it as the second clip's first-frame keyframe, so the motion appears continuous.

Use this only where the script genuinely wants a continuous move — overusing it
makes everything feel like one endless drifting take and fights the
cut-to-cut documentary rhythm. Most beats are independent shots anchored by
Mechanisms 1–2; chaining is the exception.

### Continuity is gated (Stage B5)

After generation, eyeball each recurring location across its beats: same wood
tone, same light direction, same palette. Drift means the bible wasn't pinned or
the anchor wasn't attached — fix the prompt/keyframe and regenerate just the
drifted clips (cheap; they're individual beats).

## Putting it together (per body segment)

```
body_<n>.mp3  ──segment_beats.py──▶  beats_<n>.json   (timed, verbatim sentences)
      │
      ├─ enforce one-visual rule (split/abstract/list)        [this file, Part 1]
      ├─ write iPhone B-prompt per beat                        [iphone-broll-doctrine.md]
      ├─ inject continuity bible verbatim into every prompt    [this file, Part 2.1]
      ├─ set anchor_keyframe / chain_from where needed         [this file, Part 2.2–2.3]
      └─ period-authenticity panel on every prompt             [period-authenticity-panel.md]
                         │
                         ▼
              broll_manifest.json beats[]  ──▶  batch_generate.py (waves of 5)
                         │
                         ▼
              trim_and_place.py  ──▶  body_<n>.mp4  ──▶  parent Stage 8 concat
```
