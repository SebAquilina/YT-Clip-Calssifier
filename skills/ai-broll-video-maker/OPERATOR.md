# OPERATOR PROMPT — paste this into a new chat to make one video hands-free

You make ONE faceless "Candice's Country Candles" YouTube video end-to-end with the
`ai-broll-video-maker` skill (FORMAT v7.1). The human will just tell you **which video** (a title or
row number from the ideation workbook). Do everything below, give a progress update every ~5 minutes,
and do not stop until the final video + thumbnails are delivered and copied to the Desktop.

## Prerequisites (must exist in this environment)
- This repo, on branch `claude/10-candle-hacks-video-xijwmv` (the skill lives in
  `skills/ai-broll-video-maker/`, the engine in `video_dollartree_build/`).
- Env var `LABS69_API_KEY` = the 69labs API key.
- Env var `IDEATE_XLSX` = absolute path to the ideation xlsx (the workbook with the 70 titles).
- ffmpeg/ffprobe at /usr/local/bin, python3 with openpyxl, faster-whisper, insightface (already set up
  in the standard environment). If `openpyxl` is missing: `pip install -q openpyxl`.

## When the human says e.g. "Make video: Don't Start a Candle Business" (or "do #7")
1. **Read the skill first** (do not skip): `skills/ai-broll-video-maker/SKILL.md` (FORMAT v6 → v7.1),
   `PIPELINE.md`, `references/retention-playbook.md`, `references/grok-video-th.md`,
   `references/image-visuals.md`.
2. **Pull the blueprint:** `python3 video_dollartree_build/blueprint_parse.py "$IDEATE_XLSX" "<title>"`.
   Note the MUST-COVER topics (in order), the intro hook, the ebook topic, target length, retention notes.
3. **Author the build script** `video_dollartree_build/build_<slug>.py` (copy the shape of
   `build_candlebiz.py`). Rules that MUST hold (the linter enforces them):
   - Map the MUST-COVER topics **in order** onto the Yoder 15-beat skeleton; tag retention beats with
     `role=` (cold_open, withheld/dark_loop/promise ×≥2, reframe, mechanism, step, escalation ×≥3, story,
     honesty, villain + "not a conspiracy", stakes, recap, future_pace, comment_bait, sequel_hook, signoff).
   - `coin("<one phrase>")` and repeat it ≥2×; cold open is present-tense with a number in the first ~20s.
   - Ebook CTA via `cta_ebook(...)` within the first ~1:30 (two TH beats, different scenes, says "ebook").
   - End on `SIGNOFF`. Keep TH ~12–14%, never two body THs adjacent, lines short (≤17 words TH / ≤20 VO).
   - `finalize(".../video_<slug>_veo")`.
4. **Subject continuity agents (best quality):** spawn TWO subagents per FORMAT v6.5 — Agent 1 Subject
   Director, Agent 2 Continuity Supervisor — writing `director_response.json` + `supervisor_response.json`
   into `video_<slug>_veo/Project files/agent_io/`. (The driver also runs `subject_agents.py`, which falls
   back to the heuristic if you skip this.)
5. **Run the driver (does everything else + saves to Desktop):**
   ```
   LABS69_API_KEY="$LABS69_API_KEY" IDEATE_XLSX="$IDEATE_XLSX" \
   bash skills/ai-broll-video-maker/scripts/make_video.sh \
        video_dollartree_build/build_<slug>.py  video_<slug>_veo  "<title>"
   ```
   It runs: build → **script_lint HARD GATE** (fix the script if it fails) → subject agents → generate
   (resumable, rides API congestion) → face + truncation/lead-in/muted gates → assemble (grok TH 10s +
   faster-TH + grain) → master (−16 LUFS) → description+chapters → tags → thumbnails (2×3 @2k) →
   deliverable zip (hosted) → **copy FINAL_mastered.mp4 + the zip to `~/Desktop`**.
6. **QC before declaring done:** spot-check a few grok TH frames for lip-sync/identity and a few stills for
   realism/grain. If a clip is bad: delete that beat's asset from `state.json`, re-run the driver (it's
   resumable), and re-gate. Grok's lip-sync from a still is the known weak spot — check it.
7. **Deliver:** post the hosted links (from the driver output) and confirm the files on the Desktop.

## The Desktop save (also runnable on its own)
The driver copies the result to `~/Desktop`. To copy any finished video manually:
```
cp video_<slug>_veo/FINAL_mastered.mp4 ~/Desktop/"<title>.mp4"
```
(On a local machine that's your real Desktop; in a cloud container it's the container's `~/Desktop` —
the driver also hosts the zip and prints download links, and you can use SendUserFile to push the files.)

## Notes
- TH (full + split) = grok-imagine-video 10s/720p with the fixed voice; b-roll/come-to-life = veo-lite;
  stills = nano-banana-pro 1k + grain; thumbnails = nano-banana-pro 2k.
- If 69labs is rate-limited/congested, the generate step retries across passes — be patient, keep the
  driver running; it's resumable so nothing is lost.
- One video at a time. Re-run the whole thing for the next title.
