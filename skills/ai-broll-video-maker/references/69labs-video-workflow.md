# 69labs video workflow — detailed reference (field-tested)

The exact browser workflow for generating Veo clips on 69labs.vip, updated
from a live production run. Follow the numbered recipes literally — every
snippet here is copy-paste ready and was verified working. Element refs
change on every reload: re-find controls with `find` each session.

## The page

`https://69labs.vip/videos` — "Video Generation". You must be logged in
(check for the account name top-right). Key controls:

- **Prompt textarea** — placeholder "Describe the video you want to generate"
  (limit 15,000 chars).
- **MODEL dropdown** — options seen live: **Veo 3.1 Lite**, Gemini Omni,
  Veo Fast (BETA), Grok Video (BETA). Use **Veo 3.1 Lite** (1 credit, the
  user's "VO 3.1 light"; their successful history is on it — the Veo Fast
  BETA jobs in their history FAILED). Verify the dropdown text before every
  submit; if an option is named slightly differently, pick the closest
  "Veo 3.1 Lite/Fast" and tell the user which you used.
- **ASPECT dropdown** — 16:9 (default) or 9:16. No duration control: clips
  come out 8s at 1280×720, 24fps, with audio.
- **MUTE / Strip button** — leave OFF (not pressed). Audio must stay on:
  revoice needs the original speech envelope for lip timing.
- **KEYFRAMES 0/2** strip — the reference-image mechanism (first/last
  frame). Slot 1 = first frame = your character anchor for Mode A. There is
  a small add-image (+) button next to the badge, a hidden
  `<input type=file accept="image/...">`, and once attached, a thumbnail
  with a "Remove First Frame" X button.
- **Generate button** — submit; shows credit cost.
- **Quota chips** — "Hour N left of 10 · resets HH:MM" and "Month N left of
  100", plus a Healthy / Having Issues chip. The hard budget is **10
  videos/hour**: a successful submit decrements Hour by 1; a CANCELLED job
  is refunded.
- **Gallery** — tiles PENDING → PROCESSING → COMPLETED/FAILED/CANCELLED.
  NOTE: each tile's status string appears TWICE in `document.body.innerText`
  ("PENDING,PENDING" = ONE pending tile, not two).
- **Jobs page** — `https://69labs.vip/jobs?type=videos`: list with per-job
  View / Cancel (processing) / Download + Copy URL + Delete (completed).

**State persistence:** the attached keyframe and selected model PERSIST
server-side across reloads and navigation on this page (unlike the images
page). Still verify both after every reload — takes one JS call:

```js
'model: '+document.body.innerText.match(/Veo [^\n]*/)?.[0]
 +' | '+document.body.innerText.match(/Keyframes\s*\d\/\d/i)?.[0]
 +' | turnstile: '+document.body.innerText.includes('Success!')
```

## Recipe 0 — pre-crop the reference photo (MANDATORY for Mode A)

Veo follows the reference image's shape. A square reference photo in a 16:9
job produces a **pillarboxed video** (black side bars) — the site even warns
"reference images do not match the selected aspect ratio". Before uploading,
crop the character photo to the output aspect:

```python
from PIL import Image
im = Image.open(REF_PHOTO)
w, h = im.size
th = int(w * 9 / 16)                  # 16:9; use w*16//9 logic inverted for 9:16
top = max(0, int(h * 0.18))           # bias upward to keep the face
if top + th > h: top = h - th
im.crop((0, top, w, top + th)).save(OUT_JPG, quality=92)
```

View the crop (Read the jpg) to confirm the face is fully in frame. Save the
crop inside a folder the Chrome extension can upload from (a connected
folder). After attaching, if the page shows the aspect-mismatch warning
text ("do not match the selected aspect ratio") — the crop is wrong; fix it
before generating.

## Recipe 0b — reference image constraints (learned live)

- **Exact aspect ratio**: 1.792 is NOT 16:9 (1.778) — the site flags any
  mismatch and Veo follows the reference shape. Crop to exactly 16:9
  (`int(h*16/9)` wide) before upload.
- **Size cap ~5 MB**: a larger file is silently rejected (the input clears,
  badge stays 0). Resize to 1920×1080 — plenty for 720p output.

## Recipe 1 — attach the keyframe (exact working sequence)

**SOLVED (v24/25): set the video keyframe FULLY HEADLESS — no manual drag.** The video
Keyframes box does NOT consume a `file_upload` inject (the file sets, `files=1`, but the
React onChange never uploads). The reliable way is to POST the file to the upload API and
write the returned hosted URL into the composer's localStorage — the composer hydrates
keyframes from `imageUrls` on load:

1. Put the (pre-cropped 16:9) keyframe into a file input on /videos so the page holds a
   File: `find "keyframe image file input"` -> Chrome `file_upload` it.
2. POST it + inject the URL (ONE JS call):
```js
(async()=>{const inp=[...document.querySelectorAll('input[type=file]')].find(i=>i.files&&i.files.length);
const fd=new FormData();fd.append('file',inp.files[0],inp.files[0].name);
const d=await (await fetch('/api/videos/upload',{method:'POST',body:fd})).json(); // -> {url:"https://useruploaded.69labs.vip/uploads/<hash>.jpg"}
const ls=JSON.parse(localStorage.getItem('69labs.videos.composer.v1')||'{}');
ls.imageUrls=[d.url];                       // replace first-frame; use [] to CLEAR
localStorage.setItem('69labs.videos.composer.v1',JSON.stringify(ls));return d.url;})()
```
3. **Reload /videos.** KEYFRAMES now reads 1/2 with your image (verify with the badge
   regex). To swap keyframes between clips, POST the new file and overwrite `imageUrls`.
   To clear, set `imageUrls=[]` + reload (the "Remove First Frame" button is unreliable;
   localStorage always works).

The IMAGES-page reference uploader (img2img / thumbnails) is different — it DOES accept
the legacy sequence below (or just POST `/api/videos/upload`, which returns a useruploaded
URL for any image). Legacy video-keyframe sequence (kept for reference; prefer the method
above):

The keyframes widget is a React control; neither plain `file_upload` alone
nor a change event alone registers. This three-step sequence works:

1. **Patch away the native file chooser** (once per page load) — otherwise
   clicking the + button opens an OS dialog you cannot see or close:

```js
window.__dynInputs=[]; 
const orig=HTMLInputElement.prototype.click;
HTMLInputElement.prototype.click=function(){
  if(this.type==='file'){ window.__dynInputs.push(this); return; }
  return orig.apply(this,arguments);
};
'patched'
```

2. **Inject the file** with the Chrome `file_upload` tool into the keyframe
   file input (find it with `find "keyframe file input"`). The badge will
   STILL read 0/2 — expected; keep going.

3. **Click the + (add keyframe) button** next to the KEYFRAMES badge (this
   arms the slot; the patch suppresses the chooser), then **dispatch a
   change event** and verify:

```js
const inp=document.querySelector('input[type=file]');
inp.dispatchEvent(new Event('change',{bubbles:true}));
'files='+inp.files.length
```

Wait 3–4 s, then check `document.body.innerText.match(/Keyframes\s*\d\/\d/i)`
→ must be **1/2**, and a `POST /api/videos/upload` (200) appears in
`read_network_requests`. If still 0/2, **swap the order** — both orders have worked on different days: (a) inject file → click + → dispatch, or (b) click + (arm) → inject file → dispatch. The upload only registers when the slot was armed by the button click; one retry with the other order always succeeded in production.

**Removing** (before Mode B): `find "remove keyframe X button"` → click
"Remove First Frame" → verify 0/2. A leftover reference paints the
character into b-roll.

## Recipe 2 — inject the prompt

React textarea — plain `.value=` is ignored; form-fill tools echo the whole
prompt back into your context. Use the native setter:

```js
const ta=document.querySelector('textarea');
const set=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
set.call(ta, `PROMPT TEXT AS A TEMPLATE LITERAL`);
ta.dispatchEvent(new Event('input',{bubbles:true}));
'len='+ta.value.length
```

Mode A prompts must use the keyframe pattern (the site's own successful job
history uses it): start with **"Starting from the reference image, keep the
woman, her clothing, and [the setting] exactly as shown."** then camera +
motion + colon dialogue. Do NOT re-describe her face/hair/clothes.

## Recipe 3 — submit and CONFIRM

**Submit with an in-page JS click, not a ref/coordinate click** — pixel clicks on
Generate get swallowed silently (the form submit doesn't fire):
```js
[...document.querySelectorAll('button')].find(b=>/Generate/i.test(b.textContent)).click();
```
then confirm a NEW PENDING/PROCESSING job via the jobs API. If it doesn't register, the
turnstile token expired (idle): reload, re-inject the prompt (the keyframe persists via
`imageUrls`), and JS-click immediately. **Concurrency is 1** — a second submit while one
is PROCESSING is rejected ("Concurrent video generation limit reached (1)"); submit ->
poll to COMPLETED -> capture -> next. **Monthly quota = 100**: the composer shows
"Month N left of 100"; at 0 the button reads "Monthly limit reached" and ALL video gen is
blocked until reset — read it before a batch and prioritise hook + CTA + talking heads.

1. `find "Generate submit button"` → click the ref.
2. Wait 6–8 s, then check (one JS call):

```js
document.body.innerText.match(/PENDING|PROCESSING|COMPLETED|FAILED|CANCELLED/g)?.slice(0,3).join(',')
 + ' | ' + (document.body.innerText.match(/Hour \d+ left of \d+/)?.[0]||'?')
```

A real submit = a **PENDING** tile at the front AND the Hour counter down
by 1. No PENDING tile = the submit was swallowed — see the turnstile
section before clicking again.

## Cloudflare turnstile — the #1 swallow cause

The Generate form is gated by a Cloudflare turnstile widget (bottom-right
of the composer). Healthy state shows a green "Success!" box. Two failure
modes, seen live:

- **Stale token:** one swallowed click after idling. Click Generate again —
  usually fine.
- **Challenge-platform outage:** the page looks dimmed, the turnstile box is
  EMPTY (no iframe), `document.body.innerText.includes('Success!')` is
  false, and `read_network_requests` shows
  `POST /cdn-cgi/challenge-platform/... → 503`. In this state EVERY submit
  is silently dropped (no tile, no credit). Clicking more does nothing.
  Remedy: reload the page every ~2–3 minutes until "Success!" renders, and
  use the dead time productively (revoice/verify already-captured clips).
  Observed durations: 10–30+ minutes. The ts text-check has false negatives — a submit occasionally goes through with ts:false; ALWAYS verify by the PENDING tile, never the turnstile text alone.

- **Repeated FAILED on one prompt = rephrase the dialogue.** When the same clip fails twice while others pass, the audio safety filter has latched onto the line's wording. Reword the line (different opener, same meaning) and resubmit — and update the revoice `--text` to the new wording. Failed and cancelled jobs are refunded, so count budget by the LIVE Hour counter, not attempts.

## Recipe 4 — poll and detect stuck jobs

Renders take ~2.5 min when healthy. Poll every 60–90 s with the status JS
above (10 s max per wait action — chain several, or `sleep 40` in bash
between browser calls). Decision rule, validated live:

- **> 8 minutes PROCESSING → treat as stuck.** Go to
  `https://69labs.vip/jobs?type=videos`, find the PROCESSING row, click
  **Cancel**. The credit is refunded (Hour counter goes back up).
  Navigate back to /videos and resubmit — keyframe and model persist, but
  re-inject the prompt and re-verify everything before clicking Generate.

## Recipe 5 — capture the finished clip

The newest tile's media is a `<video>` whose src is
`https://69labs.vip/api/jobs/{job-id}/stream`. Fetch → blob → download:

```js
(async()=>{
const els=[...document.querySelectorAll('video, source')]
  .map(v=>v.src||v.currentSrc)
  .filter(u=>u&&u.includes('69labs'));
if(!els.length) return 'NO_VIDEO_ELEMENTS';
const url=els[0];
if(url===window.__prevVid) return 'NOT_READY';
const r=await fetch(url); if(!r.ok) return 'FETCH_FAIL '+r.status;
const blob=await r.blob(); if(blob.size<100*1024) return 'TOO_SMALL '+blob.size;
const a=document.createElement('a');
a.href=URL.createObjectURL(blob);
a.download='clip_CHANNEL_VIDEO_SCENE_A.mp4';        // UNIQUE name per capture
document.body.appendChild(a); a.click(); a.remove();
window.__prevVid=url;
return 'OK '+blob.size+' bytes';})()
```

Baseline `window.__prevVid` BEFORE generating (set it to the current newest
URL, or null on a fresh page). Chrome never overwrites downloads — a redo
needs a fresh name (`…_v2.mp4`). Fallback: the Jobs page has a per-job
**Download** button; or Copy URL → fetch that.

**Saving:** clips land in `~/Downloads` on the host. You need access:
request the Downloads folder (`request_cowork_directory` with
`~/Downloads`) the first time. Then `cp` (NEVER `mv` — the mount rejects
deletes) into the output folder, and verify with `ffprobe`:
expect `video h264 1280x720` + `audio aac`, duration 8.0.

**Eyeball frames** (the sandbox ffmpeg is old — `-fps_mode` doesn't exist,
use `-vsync 0`):

```bash
ffmpeg -y -i clip.mp4 -vf "select='eq(n,12)+eq(n,96)+eq(n,180)',scale=640:-1" -vsync 0 f_%d.jpg
```

Copy the jpgs somewhere readable and Read them: check likeness, no
subtitles, no black side bars, B clips contain no people.

## Revoice stage — sandbox execution notes

(Full pipeline doc: the video-revoice skill. These are the traps.)

- Copy the skill to a writable dir first (`cp -r <skill>/video-revoice /tmp/revoice`).
- `faster-whisper` is REQUIRED even with `--text` (it word-times the
  ORIGINAL clip): `pip install faster-whisper --break-system-packages`.
  First run downloads the `base.en` model (~75 MB) — pre-warm it:
  `python3 -c "from faster_whisper import WhisperModel; WhisperModel('base.en',device='cpu',compute_type='int8')"`.
- Sandbox bash calls hard-cap at 45 s and **background/nohup jobs are
  killed** — run revoice synchronously with `timeout 43`. An 8 s clip
  completes in ~15–25 s once the model is cached.
- **TTS orphan 409s**: a run killed mid-TTS leaves a server-side job; the
  retry then gets `HTTP 409: A matching TTS job is already in progress`.
  Patch tts_69labs.synthesize to persist its job id (env `TTS_JOB_FILE`):
  if the file exists, resume polling that id instead of creating; write the
  id right after create. Then a killed run resumes instead of orphaning.
  The same pattern applies to VM3's narration TTS — if a paragraph 409s,
  wait ~60s for the orphan to finish, or create jobs for the remaining
  paragraphs directly via the API (create_job/get_status/download to
  `state/runs/<topic>/audio/para_NNN.mp3`) and let the paragraph cache
  skip them.
- Success looks like: `[verify] lip-sync coverage 9x% final_lufs=-1x.x`.
  Coverage ≥ 90% is good; lower → listen and consider regenerating.

## Troubleshooting table

| Symptom | Cause | Fix |
|---|---|---|
| Clicked Generate, no PENDING tile, Hour unchanged | Turnstile stale or 503 outage | Check turnstile state; reload; retry when "Success!" shows |
| Page dimmed, empty Cloudflare box, no "Success!" | challenge-platform 503 outage | Wait + reload every 2–3 min; don't keep clicking |
| Badge stays 0/2 after file_upload | React slot not armed | Recipe 1 step 3: click + then dispatch change |
| OS file chooser opened on user's screen | Clicked + without the click patch | Apply the patch (Recipe 1 step 1) on every page load BEFORE touching keyframes |
| Output video has black side bars | Reference aspect ≠ output aspect | Pre-crop the reference (Recipe 0); regenerate |
| Aspect-mismatch warning banner after attach | Same | Same |
| PROCESSING > 8 min | Stuck job | Jobs page → Cancel (credit refunded) → resubmit |
| "PENDING,PENDING" in status check | One tile (status text duplicated) | Not a double submit — count tiles, not matches |
| Capture returns NOT_READY | Still rendering | Poll again in 60–90 s |
| FAILED tile | Often the audio safety filter | Rephrase the dialogue line, resubmit (budget!) |
| Character in a B clip | Keyframe still attached | Remove First Frame, verify 0/2, regenerate |
| `mv` from Downloads fails | Mount rejects deletes | Use `cp` |
| bash `sleep 90` times out | 45 s call cap | `sleep 40` per call, several calls |
| Background pip/python dies silently | Sandbox kills detached children | Run synchronously with `timeout 43`, retry-loop installs |


## TTS at scale — bulk-queue the narration (field-tested)

Driving VM3's per-paragraph TTS loop serially through 40-second windows is
slow and orphan-prone. The fast pattern: use the skill's tts_69labs module
directly to CREATE jobs for ALL missing paragraphs in one call (they queue
server-side concurrently), wait ~60–90s, then poll+download each COMPLETED
job to `state/runs/<topic>/audio/para_NNN.mp3` in a second call. An
18-paragraph script narrates in ~2 minutes instead of ~15. Then re-run
`make.py plan` — the paragraph cache picks the files up. If a create 409s
("matching job already in progress"), an orphan exists for that text: wait
60s and retry, or find-and-poll it.

## Provider reality check (one bad night's data)

Outages can take out an entire evening: the Cloudflare turnstile blocked
ALL submits for 3+ hours, Google models (Veo, Nano Banana image gen) were
down separately (site warning), GPT Image 2 failed every attempt, and the
site auto-switched its default video model to Grok Video (BETA, 10s clips,
more credits). Fallback ladder for video: Veo 3.1 Lite → Grok Video (space
generations for credit cost). For the keyframe cleanup image: GPT Image 2 →
Nano Banana 2 — use WHICHEVER currently completes; check the gallery's
recent FAILED tiles per model before choosing. And the prime directive from
the user: when 69labs is down, SHIP THE VIDEOS without generated clips and
top them up later — pre-cut splice segments make retrofitting cheap.

## Field notes (validated 2026-06-11, videos 20–22)

- **Capture clips via `directFileUrl`, not browser downloads.** Chrome
  silently blocks the site's automatic downloads after ~5 files, and the
  /api/jobs/{id}/stream endpoint 503s during degradation. The jobs API
  (`fetch('/api/jobs?limit=N')` in-page) returns a public CDN URL per
  completed job (`directFileUrl` on vids.69labs.vip) — `curl` it straight
  from the sandbox. This is now the PRIMARY capture path; blob downloads
  are the fallback.
- **Keyframe slot refusing to arm = turnstile overlay.** If file_upload +
  click-+ + dispatch leaves KEYFRAMES at 0/2 and no upload POST appears in
  the network log, screenshot the page: if it is dimmed with the
  Cloudflare widget spinning, the overlay is eating events. Wait for
  "Success!", reload if needed (the armed reference SURVIVES reloads
  server-side), then redo: find fresh ref → file_upload → click + →
  dispatch change → verify 1/2.
- **"Complete the Turnstile verification" on Generate even when the widget
  shows Success** = expired token. Reload the page, wait for a fresh
  Success, retype the prompt, submit immediately. Submissions land
  reliably within seconds of a fresh token.
- **Server-side FAILED jobs happen** ("This job failed to complete") even
  after queuing 30+ minutes — poll `status` and resubmit; the re-run
  usually processes immediately.
- **Poll with the jobs API, not screenshots** — cheaper and shows
  queuePosition, status, userMessage and directFileUrl in one shot.
