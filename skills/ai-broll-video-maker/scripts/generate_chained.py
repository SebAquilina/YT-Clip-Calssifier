#!/usr/bin/env python3
"""generate_chained.py  (run inside a project's "Project files" dir)
FORMAT v4 generator with TALKING-HEAD FRAME-CHAINING.
- Talking heads are grouped into RUNS of consecutive character beats. The first
  clip of a run starts from the canonical th_keyframe_url; each subsequent clip's
  keyframe is the LAST FRAME of the previous clip in the run (hosted on litterbox)
  -> the run plays as one continuous take (no micro-jumps / ghost).
- B-roll beats generate independently (generic=text-to-video, character=ref keyframe).
- ONE TTS per gap. Wave scheduler keeps <=5 jobs in flight; chains advance as their
  clips complete. Fully resumable (hosted frame URLs + job status saved)."""
import json, os, time, urllib.request, urllib.error, subprocess
BASE="https://69labs.vip/api/v1"; KEY=os.environ["LABS69_API_KEY"]
ROOT=os.getcwd(); VID=os.path.dirname(ROOT)
SRC=os.path.join(VID,"Source clips"); AUD=os.path.join(ROOT,"audio")
FF="/usr/local/bin/ffmpeg"; FP="/usr/local/bin/ffprobe"; MAX=5
os.makedirs(SRC,exist_ok=True); os.makedirs(AUD,exist_ok=True)
M=json.load(open(os.path.join(ROOT,"manifest.json"))); SP=os.path.join(ROOT,"state.json")
state=json.load(open(SP)) if os.path.exists(SP) else {"beats":{},"gaps":{},"frames":{}}
for k in ("beats","gaps","frames"): state.setdefault(k,{})
def save(): json.dump(state,open(SP,"w"),indent=2)
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
REF=M["reference_photo_url"]; THKF=M.get("th_keyframe_url",REF); V=M["narrator_voice"]
HANDS=M.get("hands_ref_url",REF)
def req(method,path,body=None,t=60):
    url=path if path.startswith("http") else BASE+path
    data=json.dumps(body).encode() if body is not None else None
    h={"Authorization":f"Bearer {KEY}","User-Agent":UA,"Accept":"application/json"}
    if data:h["Content-Type"]="application/json"
    r=urllib.request.Request(url,data=data,headers=h,method=method)
    for _ in range(5):
        try:
            with urllib.request.urlopen(r,timeout=t) as resp: return resp.status,json.loads(resp.read())
        except urllib.error.HTTPError as e:
            b=e.read().decode()[:200]
            if e.code==429: time.sleep(8); continue
            return e.code,{"error":b}
        except Exception: time.sleep(4)
    return 0,{"error":"x"}
def dur(p):
    o=subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip()
    try:return float(o)
    except:return 0.0
def tts(text,dest):
    if V["provider"]=="minimax-clone":                       # 69labs Voice Clones endpoint
        body={"voiceCloneId":V["voiceCloneId"],"text":text,"model":V.get("model","speech-02-hd")}
        if V.get("speed"): body["speed"]=float(V["speed"])
        if V.get("language_boost"): body["language_boost"]=V["language_boost"]
        st,j=req("POST","/voice-clones/generate",body)
    else:
        body={"text":text,"voiceProvider":V["provider"],"voiceId":V["voiceId"],"modelId":V["modelId"]}
        if V.get("speed"): body["voiceSettings"]={"speed":float(V["speed"])}
        st,j=req("POST","/tts/generate",body)
    jid=j.get("id")
    if not jid: print("  TTS fail",j); return False
    for _ in range(60):
        time.sleep(3); st,s=req("GET",f"/tts/status/{jid}")
        if s.get("status")=="COMPLETED": break
        if s.get("status") in("FAILED","CENSORED"): return False
    r=urllib.request.Request(f"{BASE}/tts/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
    with urllib.request.urlopen(r,timeout=120) as resp,open(dest,"wb") as f: f.write(resp.read())
    return os.path.getsize(dest)>2000
def _luma(path):
    r=subprocess.run([FF,"-i",path,"-vf","signalstats,metadata=print:key=lavfi.signalstats.YAVG","-f","null","-"],capture_output=True,text=True)
    for ln in r.stderr.splitlines():
        if "YAVG" in ln:
            try: return float(ln.split("=")[-1])
            except: pass
    return 128.0
def host_frame(clip):
    """Extract the EXACT last frame of the clip for seamless chaining, with a
    black-guard fallback: if the final frame is near-black (a fade), step back a
    little so we never seed the next clip from a degraded frame."""
    jpg=f"/tmp/_chainframe_{os.getpid()}_{int(time.time()*1000)%100000}.jpg"
    chosen=None
    for off in (0.04,0.18,0.34):                  # exact last frame first, then step back
        subprocess.run([FF,"-y","-sseof",f"-{off}","-i",clip,"-frames:v","1","-vf","scale=1280:720",jpg],capture_output=True)
        if not os.path.exists(jpg): continue
        chosen=jpg
        if _luma(jpg)>=18:                        # not a near-black fade -> keep this (closest to end)
            break
    if not chosen or not os.path.exists(jpg): return None
    for _ in range(4):
        r=subprocess.run(["curl","-s","-m","90","-F","reqtype=fileupload","-F","time=72h",
            "-F",f"fileToUpload=@{jpg}","https://litterbox.catbox.moe/resources/internals/api.php"],capture_output=True,text=True)
        u=r.stdout.strip()
        if u.startswith("http"): os.remove(jpg); return u
        time.sleep(5)
    os.path.exists(jpg) and os.remove(jpg); return None
def submit(prompt,muted,mode,kf):
    body={"prompt":prompt,"model":M["video_model"],"aspectRatio":M["aspect"]}
    if muted: body["mute"]=True
    if mode!="text": body["imageUrls"]=[kf]; body["videoInputMode"]=mode
    st,j=req("POST","/videos/generate",body)
    return (j.get("id"),None) if j.get("id") else (None,j.get("error",j))
def dl(jid,dest):
    r=urllib.request.Request(f"{BASE}/videos/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
    with urllib.request.urlopen(r,timeout=180) as resp,open(dest,"wb") as f: f.write(resp.read())
    return os.path.getsize(dest)

# ---- Stage A: gap TTS ----
print("== Stage A: gap TTS ==",flush=True)
for gid,text in M["gaps"].items():
    g=state["gaps"].setdefault(gid,{}); d=os.path.join(AUD,f"gap_{gid}.mp3")
    if g.get("done") and os.path.exists(d): continue
    print("  TTS gap",gid,flush=True)
    if tts(text,d): g.update(done=True,file=d,dur=dur(d)); save()
save()

# ---- build TH runs + broll list (chains come from the manifest in v5) ----
beats=M["beats"]
if M.get("chains"):
    runs=[c["beat_ids"] for c in M["chains"]]
    chain_seed={ri:c["seed_keyframe_url"] for ri,c in enumerate(M["chains"])}
else:
    runs=[]; cur=[]
    for b in beats:
        if b["type"]=="character": cur.append(b["id"])
        elif cur: runs.append(cur); cur=[]
    if cur: runs.append(cur)
    chain_seed={ri:THKF for ri in range(len(runs))}
broll=[b for b in beats if b["type"]=="broll"]
def done(bid):
    j=state["beats"].get(bid,{}).get("job",{}); return j.get("status")=="downloaded" and j.get("file") and os.path.exists(j["file"])
for b in beats: state["beats"].setdefault(b["id"],{}).setdefault("job",{"status":"pending","job_id":None,"file":None})
save()
prompt_of={b["id"]:b for b in beats}
# run cursors: idx into run, keyframe url for the next clip
runpos={ri:0 for ri in range(len(runs))}
# advance past already-done leading clips, recover keyframe
for ri,run in enumerate(runs):
    i=0
    while i<len(run) and done(run[i]): i+=1
    runpos[ri]=i
def run_next_kf(ri):
    i=runpos[ri]
    if i==0: return chain_seed[ri]
    prev=runs[ri][i-1]
    if state["frames"].get(prev): return state["frames"][prev]
    # need to host prev's last frame
    f=state["beats"][prev]["job"].get("file")
    if f and os.path.exists(f):
        u=host_frame(f)
        if u: state["frames"][prev]=u; save(); return u
    return None

bq=[b["id"] for b in broll if not done(b["id"])]
total=len(beats); inflight={}  # jid -> ("th",ri) or ("br",bid)
deadline=time.time()+60*55
print(f"== {len(runs)} TH-runs, {len(broll)} broll; {sum(1 for b in beats if not done(b['id']))} to generate ==",flush=True)
def all_done(): return all(done(b["id"]) for b in beats)
while not all_done() and time.time()<deadline:
    # fill slots
    progressed=True
    while len(inflight)<MAX and progressed:
        progressed=False
        # advance runs (one inflight per run)
        for ri in range(len(runs)):
            if len(inflight)>=MAX: break
            if any(k==("th",ri) for k in inflight.values()): continue
            i=runpos[ri]
            if i>=len(runs[ri]): continue
            bid=runs[ri][i]
            if done(bid): runpos[ri]+=1; progressed=True; continue
            kf=run_next_kf(ri)
            if not kf: continue
            b=prompt_of[bid]
            jid,err=submit(b["prompt"],False,"keyframes",kf)
            if jid:
                state["beats"][bid]["job"].update(status="submitted",job_id=jid); inflight[jid]=("th",ri)
                print(f"  submit TH {bid} run{ri}[{i}] {jid[:8]} ({len(inflight)})",flush=True); save(); time.sleep(13); progressed=True
            else:
                es=str(err)
                if not("Concurrent" in es or "FORBIDDEN" in es): print(f"  FAIL {bid} {es[:80]}",flush=True)
                break
        # fill remaining with broll
        while len(inflight)<MAX and bq:
            bid=bq[0]
            if done(bid): bq.pop(0); continue
            b=prompt_of[bid]
            jid,err=submit(b["prompt"],True,"keyframes",HANDS)   # B-roll = her hands in her workspace
            if jid:
                state["beats"][bid]["job"].update(status="submitted",job_id=jid); inflight[jid]=("br",bid); bq.pop(0)
                print(f"  submit BR {bid} {jid[:8]} ({len(inflight)})",flush=True); save(); time.sleep(13); progressed=True
            else:
                es=str(err)
                if "Concurrent" in es or "FORBIDDEN" in es: break
                print(f"  FAIL {bid} {es[:80]}",flush=True); bq.pop(0)
    # poll
    fin=[]
    for jid,(kind,ref) in list(inflight.items()):
        st,s=req("GET",f"/videos/status/{jid}"); status=s.get("status")
        if status=="COMPLETED":
            bid = runs[ref][runpos[ref]] if kind=="th" else ref
            dest=os.path.join(SRC,f"{bid}.mp4")
            try: sz=dl(jid,dest)
            except Exception as e: print("dl err",e); continue
            if sz>100*1024:
                state["beats"][bid]["job"].update(status="downloaded",file=dest); print(f"  DONE {bid}",flush=True)
                if kind=="th":
                    u=host_frame(dest)            # host last frame for the next clip in the chain
                    if u: state["frames"][bid]=u
                    runpos[ref]+=1
            else:
                state["beats"][bid]["job"].update(status="pending",job_id=None)
                if kind=="br": bq.append(bid)
            fin.append(jid); save()
        elif status in("FAILED","CANCELLED"):
            bid = runs[ref][runpos[ref]] if kind=="th" else ref
            state["beats"][bid]["job"].update(status="pending",job_id=None)
            if kind=="br": bq.append(bid)
            print(f"  {status} {bid} requeue",flush=True); fin.append(jid); save()
    for jid in fin: inflight.pop(jid,None)
    if len(inflight)>=MAX or (not progressed and inflight): time.sleep(15)
print(f"== DONE {sum(1 for b in beats if done(b['id']))}/{total} ==",flush=True); save()
