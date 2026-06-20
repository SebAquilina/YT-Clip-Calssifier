# Dollar-Tree video — frame-by-frame said↔shown audit (v1) and v2 corrections

Audited every **non-talking-head** beat of v1 against the Elias-Yoder
**literal-match rule** (`references/iphone-broll-doctrine.md`): the visual must show
the ONE concrete hero noun + state/action the sentence is about — literally, not a
themed approximation.

**v1 average correlation: 3.68 / 5** (22 visual beats).
**v2 average (re-verified): ~4.6 / 5** after rebuilding the 9 weak/mismatch beats.

## Beats that were already strong (kept as-is)

| Beat | Line (hero) | v1 score |
|---|---|---|
| b01_full | the whole haul of cheap jars/votives/tins | 5 |
| b02_live | a single lit candle, smoke curling | 4 |
| b04_full | good candle vs charred ruined one | 4 |
| b07_full | the candle's front label | 5 |
| b11_live | tall flame tunneling down the middle | 5 |
| b12_full | deep tunnel, wasted wax up the sides | 5 |
| b14_full | black soot crawling up the glass | 5 |
| b19_full | candle on a coffee table in a real room | 5 |
| b26_full | flame gone huge, jar too hot | 5 |
| b27_live | oversized flame in a thin jar | 4 |
| b29_full | a jar actually cracked, wax leaking | 5 |
| b31_full | good vs sooted-out ruin | 4 |
| b36_full | a simple VANILLA jar | 5 |

## The 9 beats fixed in v2

| Beat | v1 problem (score) | v2 correction |
|---|---|---|
| **b06_br** | hands idle, no row, no label-out (1) | hands slide a jar to the end of a **row** of identical jars, turn it label-out |
| **b15_br** | hands weighing a clean candle (1) | hands lift a **soot-stained jar to the window** and rotate it |
| **b33_br** | hands pouring/making candles (1) | finger **points at the wick**, thin vs thicker comparison |
| **b17_split** | no nose, just unlit jars (2) | extreme close-up **nose at the jar rim, eyes closed, smelling** |
| **b10_split** | melt pool not visible, side angle (3) | **top-down** lit candle, liquid pool reaching the glass edge |
| **b23_split** | opaque ceramic, no visible pool (3) | **top-down clear glass**, full even pool, clean glass |
| **b22_full** | label read amber/clove, not vanilla (3) | candle whose label clearly reads **VANILLA** |
| **b24_live** | tabletop product shot (3) | **wide dim room washed in warm candle glow**, swaying shadows |
| **b23b** | abstract value line w/ generic candle (3) | converted to a **talking-head reaction** (doctrine: abstract → TH) |

## Root-cause lessons (now in the skill)

1. **Hands B-roll defaults to "candle-making."** A keyframe of workshop hands +
   a workshop setting biases Veo to pour/stir/weigh wax regardless of the action
   asked for. Fix: state the single action arc concretely AND add an explicit
   negative — *"NOT making candles: no pouring wax, no stirring, no pitcher, no
   thermometer; the candles are FINISHED store-bought jars."* This was the single
   biggest correlation win.
2. **Melt-pool / inside-the-jar states need a top-down angle.** "Even melt pool to
   the edge" and "clean glass, no soot" are invisible from eye level — specify
   *overhead / high top-down* and a *clear glass* vessel (never opaque ceramic).
3. **Abstract lines (verdicts, value reactions, CTAs, teases) are talking-head
   candidates, not image beats.** Forcing a literal still onto "for a dollar that
   is incredible" yields a generic candle. Hand the line back to a talking head.
4. **Ultra-short utterances (≤~6 words) can come back muted** (no audio stream)
   from Veo. Pad the line to ~9–12 natural words so Veo treats it as real speech.
5. **8-second truncation still applies to the image-visuals format** — split any
   spoken line over ~18 words (TH or split TH-pane) into ≤18-word halves with a
   hard-stop on part 1.

## Quality gates run on this build
- 2-class ArcFace face scan: **28/28 face clips = Candice, 0 imposters**.
- Vision no-text/caption scan: 1 defect (b03 "scary" caption) → regenerated clean;
  **0 Veo watermarks** across all clips.
- Whisper truncation gate: 2 over-long lines (b23, b38) split and regenerated.
