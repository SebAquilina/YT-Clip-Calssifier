# 69labs PUBLIC API (canonical) — use this, not the browser workflow

The browser/extension recipe in `69labs-video-workflow.md` is superseded. 69labs
has a documented public API; drive everything through it with an API key. The
working reference client is `scripts/generate_69labs_v1api.py` (generation: TTS +
the 5-concurrent video wave scheduler, reference-image on every clip) and
`scripts/assemble_segmented_v2.py` (A/V-sync-safe assembly).

## Auth & base
- Base: `https://69labs.vip/api/v1`
- Header: `Authorization: Bearer vk_...`  **and a real browser `User-Agent`**
  (the default `Python-urllib`/`curl`-less UA is Cloudflare-blocked → error 1010;
  every call then fails with "Invalid or expired token"-style errors).
- The internal `/api/...` paths (no `/v1`) are the website's cookie-auth endpoints
  and will reject the `vk_` key — do not use them.

## Lifecycle (identical for tts / images / videos)
`POST /{type}/generate` → `GET /{type}/status/{id}` (poll) → `GET /{type}/download/{id}`
(302 → presigned URL; follow redirects).

## Video
```
POST /api/v1/videos/generate
{ "prompt": "...", "model": "veo-video", "aspectRatio": "16:9",
  "imageUrls": ["<public url>"], "videoInputMode": "keyframes"|"ingredients",
  "mute": true }            # mute B-roll (narration runs over it)
```
- `veo-video` = "Veo 3.1 Lite", 8-second clips, 16:9.
- **Max 5 concurrent jobs** → wave-schedule to ≤5 (a 6th returns FORBIDDEN
  "Concurrent video generation limit reached").
- Quota observed on the test account: 100 video credits/hour, 5000/month.
- `imageUrls` must be **publicly reachable**. Host the reference on a STABLE url
  (a file committed to a public repo, served via `raw.githubusercontent.com`);
  anonymous temp hosts (litterbox/catbox) expire mid-run and every later clip
  then fails with "URL is not valid".

## TTS
```
POST /api/v1/tts/generate
{ "text": "...", "voiceProvider": "elevenlabs"|"edgetts",
  "voiceId": "<id>", "modelId": "eleven_multilingual_v2" }
```
- Edge voices (`en-US-JennyNeural`, …) and valid ElevenLabs voice IDs work;
  MiniMax was intermittently unavailable. Arbitrary ElevenLabs IDs not in the
  account's library are rejected.

## Images (thumbnail / anchor frames)
`POST /api/v1/images/generate` with `model` (e.g. `nano-banana-2`), `aspectRatio`,
optional `imageUrls` for img2img. The image endpoint was intermittently
`SERVICE_UNAVAILABLE` during testing — retry, or fall back to a frame grabbed
from a generated clip + a text overlay.

## Error codes
`UNAUTHORIZED` (bad/missing key or blocked UA), `FORBIDDEN` (no capability or
concurrency/credit limit), `PAYMENT_REQUIRED` (out of credits), `TOO_MANY_REQUESTS`
(rate limit — respect `Retry-After`), `GONE` (output expired, 7-day retention).
