# Candice Candle Channel — Master Improvements List

A running, comprehensive list of every improvement requested for the faceless
image-visuals candle videos, with status and how each is implemented. Newest themes
at the bottom. "Engine" = `video_dollartree_build/` (imgkit.py / gen_dt_par.py /
asm_dt.py / build_dt*.py); "Skill" = `skills/ai-broll-video-maker/`.

Legend: ✅ done & in engine+skill · 🎬 applied to this 20-min video · ➡️ moving forward only

---

## A. Visual format & realism
1. ✅🎬 **Image-visuals format** — 3 image modes (full-frame + VO, split-screen TH+image,
   come-to-life animated still) plus hands B-roll, alongside talking head.
2. ✅🎬 **iPhone-on-a-real-workbench look** — every image/live/TH prompt carries the `IPHONE`
   clause: deep focus, wide ~26mm, natural light, faint grain, NO bokeh/studio/cinematic/CGI.
   Never use "shallow depth of field" (made images look like stock renders).
3. ✅🎬 **Casual camera-roll snapshot** — framing intentionally a little imperfect (slightly
   off-center/tilted, a cut-off edge); ordinary unstaged phone photo, not a product shot.
4. ✅🎬 **B-roll a notch rougher than stills** — slightly soft, faint motion blur/grain, uneven
   exposure, so it reads as genuine handheld human footage.
5. ✅🎬 **Consistent workbench** — one generated empty-workbench reference (`refs_build.py` →
   `BENCH_REF`), passed as the img2img reference on every image beat.
6. ✅🎬 **Sharp, identity-locked talking-head keyframes** — Veo uses the keyframe as the clip's
   first frame, so soft anchors = soft TH. Generate sharp scene candidates, pick best, host,
   override `SCENES`. Biggest TH-quality lever.
7. ✅🎬 **Split image at 1:1, cover-cropped** — nano-banana supports {16:9,1:1,3:4,4:3,9:16}; the
   split pane is ~square so generate 1:1 and cover-fit (never squeeze → no warp).
8. ✅🎬 **Split-screen TH pane centered on Candice's face** — assembler detects her face x and
   crops the pane around it so she is never half-cut.

## B. Audio
9. ✅🎬 **veo↔TTS volume match** — per-segment leveling so the cloned-voice narration and Veo's
   talking-head audio sit at the same loudness; final master to -16 LUFS.
10. ✅🎬 **Lip-sync fix** — the per-segment leveling now uses a sample-aligned VOLUME GAIN, not
    dynamic loudnorm (whose lookahead delayed the audio and desynced the lips).
11. ✅🎬 **TTS no longer cut off** — generous tail padding (narration + 0.6s) so the trailing
    crossfade overlaps silence, never the last word.
12. ➡️ **No background music** — `NOMUSIC` clause on every Veo clip that carries sound (talking
    head): only her voice + natural room tone, no soundtrack/score/jingle. (Baked-in music in
    already-generated clips can't be stripped without regen, so this applies to new builds.)

## C. Talking head pacing & mix
13. ✅🎬 **Awkward trailing silence cropped** — each TH/split segment is trimmed to ~0.35s after
    speech ends (silencedetect), so clips don't sit in dead air.
14. ✅ (v5.9) **Talking head capped ~30%**, full-frame-image-with-voiceover absorbs the slack.
    (This 20-min video is ~50% TH — a side effect of splitting long lines; next build authored
    at 30% from the start.)
15. ✅ (v5.9) **Intro, outro and ALL CTAs are always talking head.**
16. ✅ **Author scripts in short ≤18-word lines from the start** — avoids Veo's 8s truncation AND
    keeps TH share low (post-hoc splitting inflates TH).

## D. Calls to action
17. ✅🎬 **Book CTA after the intro** — a talking-head beat (per rule #15) right after Candice
    lays out what's coming, with the REAL book cover composited as an inset (Veo renders books
    poorly, so the real cover is overlaid), gentle fade-in, white border.

## E. Quality gates (run every build, before delivery)
18. ✅🎬 **Imposter face scan** (2-class ArcFace) — 0 wrong-face clips required.
19. ✅🎬 **Truncation / script-cutoff gate** — `small.en` whisper + tail-presence test (base.en was
    too noisy on Veo's voice). Over-long lines split, bad/muted clips re-rolled.
20. ✅🎬 **Repetition / padding gate** — flags clips where Veo repeats a phrase or pads a short
    line ("same same same"); excludes legitimately-repeated script phrases.
21. ✅🎬 **No-text / caption / watermark vision scan** — every clip-bearing beat + stills checked;
    burned-in captions/UI re-rolled, Veo watermark delogo'd.
22. ✅🎬 **Muted-clip check** — ultra-short Veo lines can return with no audio; pad to ~12 words.

## F. Generation infrastructure
23. ✅ **Concurrent generation** — single process, semaphore-capped at 5 video / 7 image / 2 TTS
    (the real account limits); flow is unaffected because the assembler always reads beats in
    manifest order.
24. ✅ **Resumable + sharded** state with merge, robust to throttling and container restarts.
25. ✅ **Chunked crossfade join** — the single 178-input filtergraph was too large for one ffmpeg
    call; join in ~16-segment chunks then join the chunks.

## G. Said↔shown correlation (Elias-Yoder literal-match)
26. ✅🎬 **Every non-TH visual depicts the ONE concrete hero noun+action of the line**, literally,
    not a themed approximation; abstract lines route to talking head.
27. ➡️ **B-roll physics** — `NOSPAWN` clause: nothing pops/spawns/materializes/appears/disappears;
    every object present from frame one; hands only move things already on the bench.

---

### Open / next
- Build the NEXT video authored at ≤30% TH with short lines from the start (cleanest path to the
  target mix without post-hoc splitting).
- Continue tightening the repetition gate to auto-exclude script-legitimate repeats.
