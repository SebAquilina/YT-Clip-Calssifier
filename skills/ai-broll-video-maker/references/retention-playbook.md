# Retention playbook (Elias-Yoder) — baked into the script-generation phase (v7.1)

Every script must satisfy TWO things, and `script_lint.py` is the hard gate that fails the build unless
both are met:
1. **CONTENT — the xlsx blueprint** (the "Script Blueprint" cell for that video): the intro hook line, the
   ebook CTA topic, the **MUST-COVER topics in order**, the target length, and the outro. Parsed by
   `blueprint_parse.py`.
2. **RETENTION — the Yoder engine**: the 15-beat skeleton + techniques below, tagged on beats with `role=`
   so they can be detected and enforced.

## The emotional engine
"Valuable knowledge was hidden from you by people who profit from your ignorance — and I, an honest
insider, am giving it back." That frame justifies length, creates the villain, and makes finishing feel
like reclaiming something. For this channel the villain is the cheap-candle status quo / course-sellers /
fragrance marketing — never invented, always "it's just how the money flows."

## The 15-beat skeleton → buildlib roles
| Yoder beat | role= | notes |
|---|---|---|
| 1 Sensory cold open | `cold_open` | TH, present tense, "you"/"right now", ONE physical detail + a number |
| 2 Withheld answer | `withheld` | name the payoff/coined rule but don't explain it yet (opens loop) |
| 3 Identity & proof | `identity` | "I am Candice… I have…" — earn the right to be heard |
| 4 Dark loop | `dark_loop` | plant the villain ("they profit when you fail") — biggest open loop |
| 5 Retention command + promise | `promise` | "stay to the end for the one mistake that…" (a LATE payoff) |
| 6 Prerequisite reframe | `reframe` | "watch this BEFORE you…"; makes the theory mandatory |
| 7 Mechanism / teach why | `mechanism` | deliver real value; NAME + a number/date for credibility |
| 8 Steps w/ Socratic why | `step` | "Skill one is wicking. Why? Because…" |
| 9 "One more thing" ×3-4 | `escalation` | numbered chapters/principles so value never feels finished |
| 10 Honest limits / safety | `honesty` | "what this won't do"; debunk a myth on your own side (trust=retention) |
| 11 Villain payoff | `villain` | close beat-4 loop: "no money in __, money in __" + "not a conspiracy" |
| 12 Stakes zoom-out | `stakes` | LATE emotional peak: health / money-over-time / family / responsibility |
| 13 Recap checklist | `recap` (+ `future_pace`) | re-deliver value; then paint them enjoying the result |
| 14 Comment bait | `comment_bait` | one specific personal question + "I read every comment" |
| 15 Sequel hook + sign-off | `sequel_hook` + `signoff` | "next time…" + the SIGNATURE sign-off (same every video) |

## Techniques (and how they're enforced/encouraged)
- **Nested, time-anchored open loops** — ≥2 loops, ≥1 resolved late. (`script_lint`: ≥2 loop roles.)
- **Specificity = credibility** — replace "cheap/a lot" with a number/year/place. (`script_lint`: a number in
  the first ~20s; aim for more.)
- **Villain / follow-the-money** + the disarming "it's not a conspiracy, just incentives". (`villain` role +
  disclaimer check.)
- **Weaponized honesty** — a "what this won't do / safety" beat. (`honesty` role.)
- **Sensory present-tense cold open** — never "hey guys". (`cold_open` role, first beat.)
- **Coined phrase / reframe** — one phrase, repeated 2-3×. (`coin()` + `script_lint` repetition check.)
- **Story tangents that prove a point / pay off a loop** — ≥1. (`story` role.) Rule: a story must prove a
  claim or pay a loop, or cut it.
- **Rhythm** — anaphora, rule of three, short declaratives to punctuate (authoring style).
- **Stakes escalation near the END** — emotional peak is late, not early. (`stakes` role placed ~80%.)
- **Identity + signature sign-off** — series belonging. (`identity` + `signoff` = `buildlib.SIGNOFF`.)
- **Future-pacing** — "by next week you'll be…". (`future_pace` role.)
- **Soft monetization** — the ebook CTA is mentioned ONCE, disarmed ("I won't mention it again"),
  within 1:30 (the v6.4 `cta_ebook` SOP).

## How the LENGTH works (don't pad — stack & withhold)
Length comes from (a) more genuine sub-topics from the blueprint MUST-COVER, (b) the "why" behind each
step, and (c) on-theme stories — never from repeating slowly. Each minute either opens a loop, pays one
off, adds a sub-topic, or tells a story that does one of those.

## SOP for the script-generation phase
1. `blueprint_parse.py <xlsx> "<title>"` → read the content spine (hook, ebook topic, MUST-COVER in order,
   retention notes, length).
2. Author `build_*.py`: map the MUST-COVER topics, IN ORDER, onto the 15-beat skeleton; tag each retention
   beat with `role=`; `coin()` one phrase and repeat it; end on `SIGNOFF`. Keep the v6/v6.3 rules (TH
   ~12%, no body-adjacent THs, short lines, ebook CTA <1:30 via `cta_ebook`).
3. `script_lint.py <project> --xlsx <xlsx> --title "<title>"` → MUST pass (0 FAIL) before generation.
4. Then the normal pipeline (subject agents → generate → gates → assemble → master → deliver).

## Ethics caution (kept from the source)
Borrow the STRUCTURE (loops, specificity, stories, honesty, stakes, sequel hooks) without overstating
facts or inventing villains. The honesty beat isn't just ethical — it's the technique that protects the
channel when viewers fact-check.
