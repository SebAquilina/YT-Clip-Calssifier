#!/usr/bin/env python3
"""
batch_generate.py — generate the body B-roll on 69labs in WAVES OF UP TO 5
concurrent jobs, resumable from the manifest.

Reads broll_manifest.json (or a beats file), submits up to --concurrency jobs at
once, polls the jobs API, captures each finished clip via its directFileUrl, and
writes status back to the manifest after EVERY job so a crash / rate-limit pause
/ VM reset resumes cleanly. Continuity keyframes (anchor_keyframe / chain_from)
are attached before submit.

Quota: the browser-observed caps are 10/hour and 100/month; the API may allow 5
CONCURRENT but still meter per hour. The client stops cleanly when the account
returns a rate-limit / quota response and leaves the rest `pending` for the next
window (offer the user a scheduled hourly task to drain the queue).

  python3 batch_generate.py --manifest broll_manifest.json --concurrency 5 \
      --model "Veo 3.1 Lite" --aspect 16:9 --out-dir "Source clips/broll"

AUTH/ENDPOINTS: capture (/api/jobs, directFileUrl) and keyframe upload
(/api/videos/upload) are field-verified in references/69labs-video-workflow.md.
The job-CREATE call is isolated in create_video_job() — confirm its path/payload
against the account's 69labs API docs and adjust ONLY that function if needed.
Set LABS69_API_KEY and (optional) LABS69_BASE_URL in the environment.
"""
import argparse, json, os, sys, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.environ.get("LABS69_BASE_URL", "https://69labs.vip")
KEY  = os.environ.get("LABS69_API_KEY", "")
_lock = threading.Lock()

def _req(method, path, body=None, headers=None, raw=False, timeout=60):
    url = path if path.startswith("http") else BASE + path
    data = None
    h = {"Authorization": f"Bearer {KEY}"} if KEY else {}
    if headers: h.update(headers)
    if body is not None and not raw:
        data = json.dumps(body).encode(); h["Content-Type"] = "application/json"
    elif raw:
        data = body
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        b = resp.read()
        return resp.status, b

def upload_image(path):
    """POST an image to /api/videos/upload -> hosted useruploaded URL (Recipe 1)."""
    import mimetypes, uuid
    boundary = "----labs" + uuid.uuid4().hex
    fn = os.path.basename(path)
    ctype = mimetypes.guess_type(path)[0] or "image/jpeg"
    payload = b"".join([
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{fn}"\r\n'.encode(),
        f"Content-Type: {ctype}\r\n\r\n".encode(),
        open(path,"rb").read(), b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ])
    st, b = _req("POST", "/api/videos/upload", body=payload, raw=True,
                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    return json.loads(b).get("url")

def create_video_job(prompt, model, aspect, keyframe_url=None):
    """Create one Veo job. The create PATH and payload field NAMES are read from
    env so confirming the account's API is a CONFIG change, not a code edit:
        LABS69_CREATE_PATH   (default /api/videos)
        LABS69_F_PROMPT      (default prompt)
        LABS69_F_MODEL       (default model)
        LABS69_F_ASPECT      (default aspectRatio)
        LABS69_F_IMAGES      (default imageUrls)   # first-frame keyframe array
    Returns the job id. Adjust env (not this function) if the docs differ."""
    path  = os.environ.get("LABS69_CREATE_PATH", "/api/videos")
    f_p   = os.environ.get("LABS69_F_PROMPT", "prompt")
    f_m   = os.environ.get("LABS69_F_MODEL", "model")
    f_a   = os.environ.get("LABS69_F_ASPECT", "aspectRatio")
    f_img = os.environ.get("LABS69_F_IMAGES", "imageUrls")
    body = {f_p: prompt, f_m: model, f_a: aspect}
    if keyframe_url:
        body[f_img] = [keyframe_url]
    st, b = _req("POST", path, body=body)
    j = json.loads(b)
    return (j.get("id") or j.get("jobId") or j.get("job_id")
            or j.get("job", {}).get("id") or j.get("data", {}).get("id"))

def job_status(job_id):
    """Return (status, directFileUrl|None). Uses the field-verified jobs API."""
    st, b = _req("GET", f"/api/jobs?limit=50&type=videos")
    for j in json.loads(b).get("jobs", json.loads(b) if isinstance(json.loads(b), list) else []):
        if str(j.get("id")) == str(job_id):
            return j.get("status","UNKNOWN"), j.get("directFileUrl")
    return "UNKNOWN", None

def download(url, dest):
    with urllib.request.urlopen(url, timeout=180) as resp, open(dest,"wb") as f:
        f.write(resp.read())
    return os.path.getsize(dest)

def load_beats(manifest_path):
    m = json.load(open(manifest_path))
    if "broll" in m:            # full ultimate_manifest.json
        return m, m["broll"]["beats"], m["broll"].get("anchor_keyframes", {})
    if "beats" in m:            # a bare beats_<n>.json
        return m, m["beats"], {}
    raise SystemExit("manifest has no beats[]")

def save(manifest_path, m):
    with _lock:
        json.dump(m, open(manifest_path,"w"), indent=2)

def remaining_quota(default=10):
    """Best-effort hourly remaining; falls back to default. Confirm endpoint."""
    try:
        st, b = _req("GET", "/api/quota")
        return json.loads(b).get("hourRemaining", default)
    except Exception:
        return default

def run_one(beat, model, aspect, out_dir, anchors, beats_by_id):
    bid = beat["id"]
    keyframe_url = None
    try:
        # continuity keyframe attach
        if beat.get("anchor_keyframe"):
            ref = anchors.get(beat["anchor_keyframe"])
            if ref and os.path.exists(ref):
                keyframe_url = upload_image(ref)
        elif beat.get("chain_from"):
            prev = beats_by_id.get(beat["chain_from"])
            if prev and prev.get("file") and os.path.exists(prev["file"]):
                # extract last frame, upload as keyframe
                lf = os.path.join(out_dir, f"{bid}_chain.jpg")
                os.system(f'ffmpeg -y -sseof -0.2 -i "{prev["file"]}" -vframes 1 '
                          f'-vf scale=1920:1080 "{lf}" >/dev/null 2>&1')
                if os.path.exists(lf): keyframe_url = upload_image(lf)

        job_id = create_video_job(beat["prompt"], model, aspect, keyframe_url)
        beat["job_id"] = job_id
        beat["status"] = "submitted"

        # poll
        t0 = time.time()
        while time.time() - t0 < 900:           # 15 min ceiling
            time.sleep(20)
            status, direct = job_status(job_id)
            if status in ("COMPLETED","SUCCEEDED") and direct:
                dest = os.path.join(out_dir, f"{bid}.mp4")
                sz = download(direct, dest)
                if sz < 100*1024:
                    return bid, "FAILED", "tiny file"
                beat["file"] = dest; beat["status"] = "generated"
                beat["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
                return bid, "generated", dest
            if status in ("FAILED","CANCELLED"):
                beat["status"] = "pending"       # leave for retry
                return bid, "FAILED", status
        beat["status"] = "pending"
        return bid, "TIMEOUT", job_id
    except urllib.error.HTTPError as e:
        if e.code in (402, 429):                 # quota / rate limit
            beat["status"] = "pending"
            return bid, "QUOTA", str(e.code)
        beat["status"] = "pending"
        return bid, "ERROR", f"http {e.code}"
    except Exception as e:
        beat["status"] = "pending"
        return bid, "ERROR", str(e)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--concurrency", type=int, default=5)
    ap.add_argument("--model", default="Veo 3.1 Lite")
    ap.add_argument("--aspect", default="16:9")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--max-this-run", type=int, default=None,
                    help="cap submissions this run (else uses hourly quota)")
    args = ap.parse_args()
    if not KEY:
        print("[error] set LABS69_API_KEY", file=sys.stderr); sys.exit(1)
    os.makedirs(args.out_dir, exist_ok=True)

    m, beats, anchors = load_beats(args.manifest)
    beats_by_id = {b["id"]: b for b in beats}
    todo = [b for b in beats if b.get("status") in (None,"pending") and b.get("prompt")]
    no_prompt = [b for b in beats if not b.get("prompt")]
    if no_prompt:
        print(f"[warn] {len(no_prompt)} beats have no prompt yet (write them in Stage B2)")

    budget = args.max_this_run if args.max_this_run is not None else remaining_quota()
    todo = todo[:budget]
    if not todo:
        print("[done] nothing to generate this window (quota or all complete)"); return
    print(f"[run] generating {len(todo)} beats, {args.concurrency}-wide, model={args.model}")

    done = 0
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = {ex.submit(run_one, b, args.model, args.aspect, args.out_dir,
                          anchors, beats_by_id): b["id"] for b in todo}
        for fut in as_completed(futs):
            bid, outcome, info = fut.result()
            print(f"  {bid}: {outcome} {info}")
            save(args.manifest, m)               # persist after every job
            if outcome == "QUOTA":
                print("[stop] account quota hit — leaving the rest pending. "
                      "Schedule an hourly task to drain broll_manifest.json.")
                break
            if outcome == "generated":
                done += 1
    save(args.manifest, m)
    pend = sum(1 for b in beats if b.get("status") in (None,"pending"))
    print(f"[wave] generated {done} this run; {pend} beats still pending.")

if __name__ == "__main__":
    main()
