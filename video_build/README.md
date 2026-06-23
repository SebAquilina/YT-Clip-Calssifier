# The 10 Candle Hacks That Saved Me $100s — AI B-roll video build

A complete ~2:51 video for the character **Candice** (candle maker), produced with
the `ai-broll-video-maker` skill against the **69labs public API** (`/api/v1`).
Every shot is AI-generated (Veo 3.1 Lite / `veo-video`) in the iPhone-real,
sentence-matched documentary style; B-roll is voiced over by the chosen narrator
voice and the talking-head clips speak on camera with a slight Australian accent.

## Pipeline (`Project files/`)
- `manifest.json` — title, narrator voice, continuity bible, and the 15 beats
  (3 character / 12 B-roll) with verbatim sentence + Veo prompt each.
- `generate.py` — resumable generator: TTS each B-roll beat, then a wave
  scheduler that keeps ≤5 concurrent Veo jobs (the account's limit), polling and
  downloading clips. Sends a browser User-Agent (the API Cloudflare-blocks the
  default `Python-urllib` UA with error 1010).
- `retts.py` — regenerate all narration audio with the manifest's current voice.
- `assemble.py` — per beat build a normalized 1280x720/24fps segment (character
  clips keep their Veo speech; B-roll clips are pooled, looped/trimmed to the
  narration length with the narration mp3 on top), then concat to the final MP4.

## Deliverables
- `The 10 Candle Hacks That Saved Me $100s.mp4` — final video (git-ignored; large).
- `Thumbnail A (with character).png` — 1280x720 thumbnail.
- `The 10 Candle Hacks That Saved Me $100s.txt` — description with chapters.
- `Source clips/` — every generated clip (git-ignored; regenerable from the manifest).

## Key API facts (this account)
- Public API base `https://69labs.vip/api/v1`, `Authorization: Bearer vk_...`.
- Video: `veo-video` ("Veo 3.1 Lite"), 8s clips, 16:9, image keyframes via
  `imageUrls` (must be **public** URLs), 5 concurrent max, 100/hr · 5000/mo.
- TTS: Edge (`edgetts`) and ElevenLabs voice IDs supported; MiniMax was down.
- Keyframe images were hosted on litterbox (URLs expire fast — re-host if a job
  returns "URL ... not valid").
