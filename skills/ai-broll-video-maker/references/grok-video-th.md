# Grok video — talking-head prompting framework (v7)

Talking heads (full-frame AND the split TH pane) are generated with **grok-imagine-video** (image-to-video
off the scene keyframe), at **10s / 720p / 16:9**. B-roll and come-to-life stills stay on **veo-lite**.
This is `imgkit.grok_th_prompt()` + `imgkit.gen_grok_video()`; routing is `engine:"grok"` on TH beats.

## Why grok for TH (and what it can't do)
Grok's strength is identity-preserving image-to-video and native audio; its documented weakness is
lip-sync from a still (rated behind Veo). So: we keyframe off a sharp scene anchor (Candice in the
workshop), keep motion gentle, request a locked medium close-up, and **QC every TH** (the truncation /
lead-in / muted gate already verifies the spoken line; lip-sync is a visual review). Live test on our
pipeline produced a clean 10s clip that spoke the exact line with audio and held her identity.

## API shape (69labs `grok-imagine-video`)
- `duration` MUST be a **string** (`"6"` or `"10"`); `resolution` `"480p"|"720p"`; `aspectRatio`
  `16:9|1:1|9:16|3:2|2:3`; **one** keyframe via `imageUrls` (`maxImageUrls=1`); NO `videoInputMode` key.
- Output carries **video + audio + an embedded mjpeg cover** — strip the cover to a clean h264+aac
  (`gen_grok_video` does `-map 0:v:0 -map 0:a:0`). Output is ~1280×704 → assembler scales to 1280×720.
- BETA / sometimes "degraded" — submit with retry/backoff; failed gens may cost quota.

## Prompt rules baked into grok_th_prompt()
1. **Keyframe supplies appearance** — do NOT re-describe her face/clothes (fighting the image causes
   drift). Prompt the MOTION + speech instead.
2. **Front-loaded, ~50 words, natural descriptive language** (not keyword stuffing) — Grok weights the
   first words most.
3. **Locked static camera, medium close-up chest up** — tight close-ups and camera moves are the most
   artifact-prone; medium framing + locked camera minimise face softening.
4. **Gentle motion only** (small head moves, natural blinks, looks into the lens) — no walking/big gestures.
5. **Affirmative stability, never negatives** — "face stays sharp and stable, exact same identity, no
   morphing" (negative prompts work poorly on Grok).
6. **`Speech: "<line>"`** — Grok's documented way to set spoken dialogue; avoids burned-in captions
   (plus an explicit "no captions or text").
7. **`Sound:` line carries the FIXED voice** — every TH injects the exact same voice sentence so all THs
   sound identical (Grok takes its voice from the prompt; there is no voice-clone here):
   > Her speaking voice is a warm, friendly, natural American accent, a clear standard General American
   > accent with no foreign or regional twang. A relaxed, even, middle-aged American woman's voice,
   > medium pitch, clear and unhurried.
   …then "Quiet natural room tone, no background music."
8. **Keep the spoken line short** (~1 sentence / our ≤17-word rule) — long speech in one clip drifts sync.

## Template (what grok_th_prompt emits)
```
She looks straight into the camera and talks warmly to the viewer, <scene>, with small natural head
movements and natural blinking, relaxed and friendly. Locked static camera, medium close-up chest up,
soft natural window light. Her face stays sharp and stable with the exact same identity the whole time,
no morphing or warping. Clean footage, no captions or text.
Speech: "<the line>"
Sound: <fixed voice sentence> Quiet natural room tone, no background music.
```

## Assembler interaction
- `engine:"grok"` → assembler **skips delogo** (no veo watermark) and still applies trailing-silence crop +
  `TH_SPEED` (1.12 video+audio together) so she speaks a touch faster with lips synced.
- 10s clips give more spoken-line headroom than veo's 8s; the silence crop trims the tail.
