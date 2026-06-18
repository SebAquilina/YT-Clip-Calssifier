#!/usr/bin/env python3
"""book_cta_th.py <out_segment.mp4> "<clip1 line>||<clip2 line>[||<clip3 line>]"

Build the e-book CTA as a REAL Candice talking-head segment (not a static card).
No nano-banana pre-compositing: the book cover is fed DIRECTLY to veo as a
reference image via videoInputMode="ingredients", together with Candice's
reference photo, so veo generates HER (face locked) holding the actual book and
telling the viewer to grab it. veo's own TH voice (matches the talking-head
sections). Up to 3 clips. Output 1280x720 / 24fps / AAC 48k so it splices in.

Per-video tailoring: pass up to 3 '||'-separated spoken lines (one per ~8s clip).
Both reference URLs are STABLE raw.githubusercontent links (ingredients refs must
not be on expiring temp hosts).
"""
import os,sys,json,time,subprocess,urllib.request,urllib.error
BASE="https://69labs.vip/api/v1"; KEY=os.environ["LABS69_API_KEY"]
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
FF="/usr/local/bin/ffmpeg"; FP="/usr/local/bin/ffprobe"
OUT=sys.argv[1]
LINES=[s.strip() for s in (sys.argv[2] if len(sys.argv)>2 else "").split("||") if s.strip()][:3]
if not LINES:
    LINES=["Oh, and one quick thing before you go. If you love making candles, I put my entire method into this little book I am holding.",
           "It is called The Three Dollar Luxury Candle, and the link is right down in the description. Go grab it, I would love to hear what you make."]
REF=open("/tmp/raw_ref.txt").read().strip()
BOOK="https://raw.githubusercontent.com/SebAquilina/YT-Clip-Calssifier/claude/10-candle-hacks-video-xijwmv/assets/book_cover.jpg"
INGREDIENTS=[REF,BOOK]            # [identity, book cover] — both stable raw URLs
WS=("an ordinary lived-in home candle workshop: a worktable with glass candle jars, bags of soy wax, "
"amber fragrance-oil bottles, a kitchen thermometer and a curing shelf of finished candles, natural daylight.")
IDENTITY=("The woman is the EXACT SAME woman shown in the first reference image — identical face, identical "
"tortoiseshell glasses, identical curly grey hair, blue knit sweater and tan apron. She is white, in her "
"mid-fifties. Do NOT change her face, age, or ethnicity into a different person. ")
# Clip 1: hold the book up clearly (sharp cover), THEN set it down on the bench near the end, so later
# clips never depend on rendering crisp cover text (which can blur when the book is held mid-motion).
BOOKHOLD_FIRST=("At the start she holds up the paperback book from the second reference image toward the camera at "
"about chest height with both hands, held steady and still so its front cover (a warm photo of a lit luxury candle "
"with the title 'The $3 Luxury Candle') faces the viewer and is crisp and clearly readable; then, near the end of "
"the clip, she gently lowers the book and sets it down flat on the workbench in front of her. ")
BOOKHOLD_REST=("The same paperback book now rests flat on the workbench in front of her, cover up and visible but "
"not held; she gestures toward it naturally now and then but keeps her hands free and does not lift it. ")
# The book's OWN printed cover is a real physical object and is allowed; nothing else is overlaid.
NOTEXT=("ABSOLUTELY NO on-screen text overlays of any kind: no subtitles, no captions, no transcription, no "
"title cards, no lower-thirds, no REC indicator, no red dot, no UI, no timecode, no watermark, no logos. The "
"ONLY printed words allowed are the real cover of the physical book she is holding and small real jar labels.")
TH_STRICT=("Exactly ONE person, a single solid subject — no second face, no double exposure, no ghosting, no "
"morphing, no extra hands; natural blink and lip-sync; steady framing. She is already mid-sentence: begins the "
"first word immediately with no inhale and speaks continuously without freezing.")

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

def th_prompt(line,first):
    hold=BOOKHOLD_FIRST if first else BOOKHOLD_REST
    return (f"Photoreal casual handheld smartphone vlog clip. {IDENTITY}She is seated at her candle workbench, "
    f"looking straight at the camera. {hold}She speaks directly to the camera in a warm American accent, lips "
    f"fully in sync, saying exactly: \"{line}\". {TH_STRICT} {NOTEXT} Setting: {WS}")
def submit(prompt):
    body={"prompt":prompt,"model":"veo-video","aspectRatio":"16:9","skipWatermarkRemoval":False,
          "imageUrls":INGREDIENTS,"videoInputMode":"ingredients"}
    st,j=req("POST","/videos/generate",body)
    return j.get("id"),(None if j.get("id") else j)
def wait_dl(jid,dest):
    for _ in range(160):
        time.sleep(6); _,s=req("GET",f"/videos/status/{jid}")
        stt=s.get("status")
        if stt=="COMPLETED":
            r=urllib.request.Request(f"{BASE}/videos/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
            with urllib.request.urlopen(r,timeout=180) as resp,open(dest,"wb") as f: f.write(resp.read())
            return os.path.getsize(dest)>20000
        if stt in("FAILED","CENSORED"): print("clip",stt,flush=True); return False
    return False

parts=[]
for i,line in enumerate(LINES):
    print(f"== CTA clip {i+1}/{len(LINES)} (ingredients: identity + book) ==",flush=True)
    raw=f"/tmp/cta_clip_{i+1}.mp4"
    ok=False
    for gen_try in range(4):                   # regenerate on transient veo FAILED
        jid=None
        for attempt in range(40):              # persistent: backend has only 5 concurrent slots
            jid,err=submit(th_prompt(line,first=(i==0)))
            if jid: break
            wait=min(12+attempt*4,45)
            print(f"  submit busy (attempt {attempt+1}), wait {wait}s: {str(err)[:90]}",flush=True); time.sleep(wait)
        assert jid, f"clip {i+1} submit failed after retries"
        if wait_dl(jid,raw): ok=True; break
        print(f"  clip {i+1} veo FAILED, regenerating (try {gen_try+2})",flush=True); time.sleep(5)
    assert ok, f"clip {i+1} failed after regeneration attempts"
    norm=f"/tmp/cta_norm_{i+1}.mp4"
    subprocess.run([FF,"-y","-i",raw,"-vf","scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=24",
        "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
        "-ar","48000","-ac","2",norm],capture_output=True)
    parts.append(norm); print(f"  clip {i+1} ready {dur(norm):.1f}s",flush=True)

# ---- concat with short crossfades (ingredients clips are independent, not frame-chained) ----
if len(parts)==1:
    subprocess.run([FF,"-y","-i",parts[0],"-c","copy",OUT],capture_output=True)
else:
    XF=0.4
    inp=[];
    for p in parts: inp+=["-i",p]
    # build xfade/acrossfade chain
    vlab="[0:v]"; alab="[0:a]"; fc=[]; acc=dur(parts[0])
    for k in range(1,len(parts)):
        off=acc-XF
        fc.append(f"{vlab}[{k}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{k}]")
        fc.append(f"{alab}[{k}:a]acrossfade=d={XF}[a{k}]")
        vlab=f"[v{k}]"; alab=f"[a{k}]"; acc=acc+dur(parts[k])-XF
    cmd=[FF,"-y"]+inp+["-filter_complex",";".join(fc),"-map",vlab,"-map",alab,
        "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","160k","-ar","48000","-ac","2",OUT]
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode!=0:
        print("xfade failed, hard concat:",r.stderr[-300:],flush=True)
        lst="/tmp/cta_parts.txt"; open(lst,"w").write("".join(f"file '{p}'\n" for p in parts))
        subprocess.run([FF,"-y","-f","concat","-safe","0","-i",lst,"-c:v","libx264","-crf","20",
            "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","48000","-ac","2",OUT],capture_output=True)
print(f"BOOK CTA (talking-head, ingredients) SEGMENT: {OUT} {dur(OUT):.1f}s ({len(parts)} clips)",flush=True)
