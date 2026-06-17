#!/usr/bin/env python3
"""book_cta_th.py <out_segment.mp4> "<clip1 line>||<clip2 line>[||<clip3 line>]"

Build the e-book CTA as a REAL Candice talking-head segment (not a static card):
  1) nano-banana-2 composes a keyframe of Candice holding her book up to camera,
     fed BOTH her reference photo AND the actual book-cover image, so the book in
     her hands matches the real cover.
  2) veo talking-head clips (max 3) chained from that keyframe — exact-last-frame
     seeding, identity-locked, veo's own TH voice (so it matches the talking-head
     sections, not the gap-narration TTS). She holds the book up the whole time
     and tells the viewer to grab it; link goes in the description.
  3) concat to 1280x720 / 24fps / AAC 48k so it splices into any video.

Per-video tailoring: pass up to 3 '||'-separated spoken lines (one per ~8s clip).
"""
import os,sys,json,time,subprocess,urllib.request,urllib.error
BASE="https://69labs.vip/api/v1"; KEY=os.environ["LABS69_API_KEY"]
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
FF="/usr/local/bin/ffmpeg"; FP="/usr/local/bin/ffprobe"
OUT=sys.argv[1]
LINES=[s.strip() for s in (sys.argv[2] if len(sys.argv)>2 else "").split("||") if s.strip()][:3]
if not LINES:
    LINES=["Oh, and one quick thing before you go. If you love making candles, I put my entire method into my little e-book.",
           "It is called The Three Dollar Luxury Candle, and the link is right down in the description. Go grab it, I would love to hear what you make."]
REF=open("/tmp/raw_ref.txt").read().strip()
BOOK="https://raw.githubusercontent.com/SebAquilina/YT-Clip-Calssifier/claude/10-candle-hacks-video-xijwmv/assets/book_cover.jpg"
WS=("an ordinary lived-in home candle workshop: a worktable with glass candle jars, bags of soy wax, "
"amber fragrance-oil bottles, a kitchen thermometer and a curing shelf of finished candles, natural daylight.")
IDENTITY=("This is the EXACT SAME woman shown in the reference keyframe image — identical face, identical "
"tortoiseshell glasses, identical curly grey hair, blue knit sweater and tan apron. She is white, in her "
"mid-fifties. Do NOT change her face, age, or ethnicity into a different person. ")
# The book's OWN printed cover is a real physical object and is allowed; everything else stays text-free.
NOTEXT=("ABSOLUTELY NO on-screen text overlays of any kind: no subtitles, no captions, no transcription, no "
"title cards, no lower-thirds, no REC indicator, no red dot, no UI, no timecode, no watermark, no logos. The "
"ONLY printed words allowed are the real cover of the physical book she is holding and small real jar labels.")
TH_STRICT=("Exactly ONE person, a single solid subject — no second face, no double exposure, no ghosting, no "
"morphing, no extra hands; natural blink and lip-sync; steady framing. She is already mid-sentence: begins the "
"first word immediately with no inhale and speaks continuously without freezing.")
BOOKHOLD=("She holds her paperback book up toward the camera at about chest height with both hands, its front "
"cover (a warm photo of a lit luxury candle with the title 'The $3 Luxury Candle') facing the viewer and clearly "
"readable, and she keeps it raised and visible the entire time. ")

def req(method,path,body=None,t=90):
    url=path if path.startswith("http") else BASE+path
    data=json.dumps(body).encode() if body is not None else None
    h={"Authorization":f"Bearer {KEY}","User-Agent":UA,"Accept":"application/json"}
    if data:h["Content-Type"]="application/json"
    r=urllib.request.Request(url,data=data,headers=h,method=method)
    try:
        with urllib.request.urlopen(r,timeout=t) as resp: return resp.status,json.loads(resp.read())
    except urllib.error.HTTPError as e: return e.code,{"error":e.read().decode()[:200]}
    except Exception as ex: return 0,{"error":str(ex)}
def dur(p):
    o=subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip()
    try: return float(o)
    except: return 0.0
def host(path):
    for _ in range(5):
        r=subprocess.run(["curl","-s","-m","120","-F","reqtype=fileupload","-F","time=72h",
            "-F",f"fileToUpload=@{path}","https://litterbox.catbox.moe/resources/internals/api.php"],capture_output=True,text=True)
        u=r.stdout.strip()
        if u.startswith("http"): return u
        time.sleep(5)
    return None
def last_frame_url(clip):
    jpg=f"/tmp/_ctaframe_{os.getpid()}_{int(time.time()*1000)%100000}.jpg"
    subprocess.run([FF,"-y","-sseof","-0.10","-i",clip,"-frames:v","1","-vf","scale=1280:720",jpg],capture_output=True)
    if not os.path.exists(jpg): return None
    u=host(jpg); os.path.exists(jpg) and os.remove(jpg); return u

# ---- 1) composite keyframe: Candice holding the book (her ref + the book cover) ----
kf_prompt=(f"Photoreal portrait of the EXACT same woman as the FIRST reference image (mid-fifties, tortoiseshell "
f"glasses, curly grey hair, blue knit sweater, tan apron), seated at her candle workbench, holding up a paperback "
f"book toward the camera with both hands at chest height. The book's front cover EXACTLY matches the SECOND "
f"reference image — a warm photo of a lit luxury candle with the title 'The $3 Luxury Candle'. She looks straight "
f"at the camera, warm and friendly, mouth slightly open as if about to speak, sharp and in focus, eye-level "
f"casual handheld framing. The only printed words in frame are the real book cover. No on-screen graphics, no "
f"REC dot, no UI, no overlays, no watermark, full-bleed photographic image. Setting: {WS}")
print("== compose keyframe (Candice + book) ==",flush=True)
st,j=req("POST","/images/generate",{"model":"nano-banana-2","aspectRatio":"16:9","prompt":kf_prompt,"imageUrls":[REF,BOOK]})
iid=j.get("id"); assert iid, f"image submit failed: {st} {j}"
kf_path="/tmp/cta_keyframe.png"
for _ in range(120):
    time.sleep(5); _,info=req("GET",f"/images/status/{iid}"); s=info.get("status")
    if s=="COMPLETED":
        rr=urllib.request.Request(f"{BASE}/images/download/{iid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
        with urllib.request.urlopen(rr,timeout=90) as resp,open(kf_path,"wb") as f: f.write(resp.read())
        break
    if s in("FAILED","CENSORED"): raise SystemExit(f"keyframe {s}")
print(f"keyframe saved ({os.path.getsize(kf_path)} bytes)",flush=True)
seed=host(kf_path); assert seed, "host keyframe failed"

# ---- 2) chained veo talking-head clips (max 3) ----
def th_prompt(line,first):
    lead=("She is seated at her candle workbench, looking straight at the camera. " if first else
          "The exact same woman continues, still holding the book up to the camera. ")
    return (f"{IDENTITY}{lead}{BOOKHOLD}She speaks directly to the camera in a warm American accent, lips fully in "
    f"sync, saying exactly: \"{line}\". {TH_STRICT} {NOTEXT} Casual handheld smartphone vlog look. Setting: {WS}")
def submit(prompt,kf):
    body={"prompt":prompt,"model":"veo-video","aspectRatio":"16:9","skipWatermarkRemoval":False,
          "imageUrls":[kf],"videoInputMode":"keyframes"}
    st,j=req("POST","/videos/generate",body)
    return j.get("id"),(None if j.get("id") else j)
def wait_dl(jid,dest):
    for _ in range(150):
        time.sleep(6); _,s=req("GET",f"/videos/status/{jid}")
        stt=s.get("status")
        if stt=="COMPLETED":
            r=urllib.request.Request(f"{BASE}/videos/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
            with urllib.request.urlopen(r,timeout=180) as resp,open(dest,"wb") as f: f.write(resp.read())
            return os.path.getsize(dest)>20000
        if stt in("FAILED","CENSORED"): print("clip",stt,flush=True); return False
    return False
parts=[]
cur_seed=seed
for i,line in enumerate(LINES):
    print(f"== CTA clip {i+1}/{len(LINES)} ==",flush=True)
    jid=None
    for attempt in range(40):                 # persistent: backend has only 5 concurrent slots (fail-gen uses them)
        jid,err=submit(th_prompt(line,first=(i==0)),cur_seed)
        if jid: break
        wait=min(20+attempt*5,60)
        print(f"  submit busy (attempt {attempt+1}), wait {wait}s: {str(err)[:120]}",flush=True); time.sleep(wait)
    assert jid, f"clip {i+1} submit failed after retries"
    raw=f"/tmp/cta_clip_{i+1}.mp4"
    assert wait_dl(jid,raw), f"clip {i+1} download failed"
    norm=f"/tmp/cta_norm_{i+1}.mp4"
    subprocess.run([FF,"-y","-i",raw,"-vf","scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=24",
        "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
        "-ar","48000","-ac","2",norm],capture_output=True)
    parts.append(norm); print(f"  clip {i+1} ready {dur(norm):.1f}s",flush=True)
    if i<len(LINES)-1:
        nf=last_frame_url(raw)
        if nf: cur_seed=nf
        else: print("  WARN: chain frame host failed, reusing keyframe",flush=True)

# ---- 3) concat ----
lst="/tmp/cta_parts.txt"
open(lst,"w").write("".join(f"file '{p}'\n" for p in parts))
ok=subprocess.run([FF,"-y","-f","concat","-safe","0","-i",lst,"-c","copy",OUT],capture_output=True,text=True)
if ok.returncode!=0:
    # fallback re-encode concat
    subprocess.run([FF,"-y","-f","concat","-safe","0","-i",lst,"-c:v","libx264","-crf","20","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","160k","-ar","48000","-ac","2",OUT],capture_output=True)
print(f"BOOK CTA (talking-head) SEGMENT: {OUT} {dur(OUT):.1f}s ({len(parts)} clips)",flush=True)
