# Running this skill on your own laptop (no GitHub required)

**Does it need GitHub?** No. GitHub is only how the code was *delivered*. At runtime the code never calls
GitHub for logic — the single GitHub reference is the default *public URL* of the keyframe images, and
those image files are already in the repo. `bootstrap_local.py` re-hosts them so even that is gone.

**Can it run fully offline?** No — and nothing can: this drives cloud AI models. It needs the internet for
two things (neither is GitHub):
- **69labs.vip** — the image / video / TTS generation API (your `LABS69_API_KEY`).
- **a public image host (litterbox.catbox.moe)** — because 69labs fetches your reference/keyframe images
  *server-side*, so any local image used as a keyframe or subject-reference must sit at a public URL.
Everything else (script authoring, the linter, assembly with ffmpeg, mastering, packaging) runs locally.

## One-time laptop setup
1. **Get the files** (any of):
   - `git clone` the repo and `git checkout claude/10-candle-hacks-video-xijwmv`, or
   - just copy the two folders you need: `video_dollartree_build/`, `video_ps_veo/assets/`,
     `video_build/assets/`, and `skills/ai-broll-video-maker/` (plus your ideation `.xlsx`).
2. **Install deps:**
   - `ffmpeg` + `ffprobe` (Homebrew: `brew install ffmpeg`) — the code expects them at
     `/usr/local/bin/ffmpeg|ffprobe` (Apple-Silicon Homebrew is `/opt/homebrew/bin`; symlink them or
     edit `FF`/`FP` in `video_dollartree_build/imgkit.py`).
   - `pip install openpyxl faster-whisper insightface onnxruntime opencv-python-headless numpy`.
3. **Set your key and bootstrap (removes the GitHub dependency):**
   ```
   export LABS69_API_KEY=vk_xxx
   python3 video_dollartree_build/bootstrap_local.py
   ```
   This hosts the 6 reference images and writes `/tmp/scene_refs.json`, `/tmp/raw_ref.txt`,
   `/tmp/bench_ref.txt`, `/tmp/apikey.txt`. (litterbox links last 72h — re-run to refresh, or host the 6
   images permanently somewhere and paste those URLs into `/tmp/scene_refs.json`.)

## Make a video
```
export LABS69_API_KEY=vk_xxx
export IDEATE_XLSX=/path/to/ideation.xlsx
bash skills/ai-broll-video-maker/scripts/make_video.sh \
     video_dollartree_build/build_<slug>.py  video_<slug>_veo  "<title>"
```
The driver auto-runs the bootstrap if needed, builds, lints (hard gate), generates, gates, assembles,
masters, packages, and copies `FINAL_mastered.mp4` + the zip to **`~/Desktop`** (your real Desktop when
run locally).

## Fully GitHub-independent / permanent option
After `bootstrap_local.py`, nothing reads GitHub. For a permanent setup, host the 6 images in `assets`
on any always-on host (your own S3/site/Cloudinary) and hard-write those URLs into `/tmp/scene_refs.json`
once — then you never depend on litterbox's 72h expiry either. The only remaining external calls are the
69labs API and uploading per-run generated images to a public host for img2img chaining.
