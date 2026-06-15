#!/usr/bin/env python3
"""Resumable 69labs generator for the 10 Candle Hacks video.
Stage A: TTS each B-roll beat (narration voice) -> audio/<id>.mp3 (+duration).
Stage B/C: a wave scheduler that keeps <=MAX_INFLIGHT video jobs running at once
(the account allows 5 concurrent), polling + downloading completed clips and
filling freed slots from the pending queue. Character beats speak their line
(audio on, slight Australian accent); B-roll beats are muted. State is saved
after every change so the run resumes cleanly.
"""
import json, os, time, math, urllib.request, urllib.error, subprocess

BASE = "https://69labs.vip/api/v1"
KEY  = os.environ["LABS69_API_KEY"]
ROOT = os.path.dirname(os.path.abspath(__file__))
VID  = os.path.dirname(ROOT)
SRC  = os.path.join(VID, "Source clips")
AUD  = os.path.join(ROOT, "audio")
FFPROBE = "/usr/local/bin/ffprobe"
MAX_INFLIGHT = 5
os.makedirs(SRC, exist_ok=True); os.makedirs(AUD, exist_ok=True)

M = json.load(open(os.path.join(ROOT, "manifest.json")))
STATE_PATH = os.path.join(ROOT, "state.json")
state = json.load(open(STATE_PATH)) if os.path.exists(STATE_PATH) else {"beats": {}}
def save(): json.dump(state, open(STATE_PATH, "w"), indent=2)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

def req(method, path, body=None, timeout=60):
    url = path if path.startswith("http") else BASE + path
    data = json.dumps(body).encode() if body is not None else None
    h = {"Authorization": f"Bearer {KEY}", "User-Agent": UA, "Accept": "application/json"}
    if data: h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    for _ in range(5):
        try:
            with urllib.request.urlopen(r, timeout=timeout) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            b = e.read().decode()[:300]
            if e.code == 429: time.sleep(8); continue
            return e.code, {"error": b}
        except Exception:
            time.sleep(4)
    return 0, {"error": "retries exhausted"}

def dur(path):
    out = subprocess.run([FFPROBE,"-v","error","-show_entries","format=duration",
        "-of","default=nk=1:nw=1",path],capture_output=True,text=True).stdout.strip()
    try: return float(out)
    except: return 0.0

VOICE = M["narrator_voice"]
def tts(text, dest):
    st, j = req("POST", "/tts/generate", {"text": text, "voiceProvider": VOICE["provider"],
        "voiceId": VOICE["voiceId"], "modelId": VOICE["modelId"]})
    jid = j.get("id")
    if not jid: print("  TTS create fail:", j); return False
    for _ in range(40):
        time.sleep(3)
        st, s = req("GET", f"/tts/status/{jid}")
        if s.get("status") == "COMPLETED": break
        if s.get("status") in ("FAILED","CENSORED"): print("  TTS", s.get("status")); return False
    r = urllib.request.Request(f"{BASE}/tts/download/{jid}",
        headers={"Authorization": f"Bearer {KEY}", "User-Agent": UA})
    with urllib.request.urlopen(r, timeout=120) as resp, open(dest,"wb") as f:
        f.write(resp.read())
    return os.path.getsize(dest) > 2000

def submit_video(prompt, muted, keyframe=None):
    body = {"prompt": prompt, "model": M["video_model"], "aspectRatio": M["aspect"]}
    if muted: body["mute"] = True
    if keyframe: body["imageUrls"] = [keyframe]; body["videoInputMode"] = "keyframes"
    st, j = req("POST", "/videos/generate", body)
    if j.get("id"): return j["id"], None
    return None, j.get("error", j)

def download_video(jid, dest):
    r = urllib.request.Request(f"{BASE}/videos/download/{jid}",
        headers={"Authorization": f"Bearer {KEY}", "User-Agent": UA})
    with urllib.request.urlopen(r, timeout=180) as resp, open(dest,"wb") as f:
        f.write(resp.read())
    return os.path.getsize(dest)

CLIP_LEN = 8.0; REF = M["reference_photo_url"]; BIBLE = M["continuity_bible"]

# ---------- Stage A: TTS ----------
print("== Stage A: TTS ==", flush=True)
for b in M["beats"]:
    bid = b["id"]; s = state["beats"].setdefault(bid, {})
    if b["type"] != "broll": s["n_clips"] = 1; continue
    dest = os.path.join(AUD, f"{bid}.mp3")
    if s.get("tts_done") and os.path.exists(dest): continue
    print("  TTS", bid, flush=True)
    if tts(b["sentence"], dest):
        d = dur(dest); s.update(tts_done=True, narration=dest, narration_dur=d,
            n_clips=max(1, math.ceil((d-0.05)/CLIP_LEN))); save()
    else: print("    FAILED", bid)
save()

# ---------- Build task list ----------
def beat_prompt(b, ci, n):
    if b["type"] == "character":
        line = b["sentence"].replace('"', "'")
        return (b["prompt"] + f" She speaks warmly to the camera with a slight Australian "
                f"accent, saying: \"{line}\". Lips move naturally in sync. Scene world: {BIBLE}")
    angles = [" Static eye-level close shot.", " Slightly higher angle, slow push-in."]
    extra = angles[ci % len(angles)] if n > 1 else ""
    return b["prompt"] + extra + f" Scene world: {BIBLE}"

tasks = []
for b in M["beats"]:
    s = state["beats"][b["id"]]; n = s.get("n_clips", 1)
    jobs = s.setdefault("jobs", {})
    for ci in range(n):
        jd = jobs.setdefault(str(ci), {"status": "pending", "job_id": None, "file": None})
        # treat clips already downloaded as done; everything else re-queue (clear stale job_id)
        if jd.get("status") == "downloaded" and jd.get("file") and os.path.exists(jd["file"]):
            continue
        jd.update(status="pending", job_id=None)
        tasks.append((b, ci, n))
save()
print(f"== {len(tasks)} clips to generate, {MAX_INFLIGHT}-concurrent ==", flush=True)

# ---------- Wave scheduler ----------
inflight = {}   # job_id -> (beat, ci)
qi = 0
deadline = time.time() + 60*55
while (qi < len(tasks) or inflight) and time.time() < deadline:
    # fill slots
    while len(inflight) < MAX_INFLIGHT and qi < len(tasks):
        b, ci, n = tasks[qi]
        muted = (b["type"] == "broll"); kf = REF if b["type"]=="character" else None
        jid, err = submit_video(beat_prompt(b, ci, n), muted, kf)
        if jid:
            state["beats"][b["id"]]["jobs"][str(ci)].update(status="submitted", job_id=jid)
            inflight[jid] = (b, ci); qi += 1
            print(f"  submit {b['id']}[{ci}] {jid[:8]} ({len(inflight)} inflight)", flush=True)
            save(); time.sleep(13)   # 5/min create limit
        else:
            es = str(err)
            if "Concurrent" in es or "FORBIDDEN" in es:
                break  # slots full server-side; go poll
            else:
                print(f"  submit FAIL {b['id']}[{ci}] {es[:120]}", flush=True)
                time.sleep(10); break
    # poll inflight
    done = []
    for jid, (b, ci) in list(inflight.items()):
        st, s = req("GET", f"/videos/status/{jid}")
        status = s.get("status")
        if status == "COMPLETED":
            dest = os.path.join(SRC, f"{b['id']}_k{ci}.mp4")
            try: sz = download_video(jid, dest)
            except Exception as e: print("  dl err", e); continue
            if sz > 100*1024:
                state["beats"][b["id"]]["jobs"][str(ci)].update(status="downloaded", file=dest)
                print(f"  DONE {b['id']}[{ci}] {sz}b", flush=True)
            else:
                state["beats"][b["id"]]["jobs"][str(ci)].update(status="pending", job_id=None)
                tasks.append((b, ci, state["beats"][b['id']].get("n_clips",1)))
            done.append(jid); save()
        elif status in ("FAILED","CANCELLED"):
            print(f"  {status} {b['id']}[{ci}] -> requeue", flush=True)
            state["beats"][b["id"]]["jobs"][str(ci)].update(status="pending", job_id=None)
            tasks.append((b, ci, state["beats"][b['id']].get("n_clips",1)))
            done.append(jid); save()
    for jid in done: inflight.pop(jid, None)
    if len(inflight) >= MAX_INFLIGHT or (qi >= len(tasks) and inflight):
        time.sleep(15)

# summary
total = down = 0
for b in M["beats"]:
    for ci, jd in state["beats"][b["id"]]["jobs"].items():
        total += 1; down += (jd.get("status") == "downloaded")
print(f"== DONE: {down}/{total} clips downloaded ==", flush=True)
save()
