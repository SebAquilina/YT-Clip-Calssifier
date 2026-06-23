#!/usr/bin/env python3
"""69labs generator v2 (face-consistent + resumable).
- Reference image is attached to EVERY clip: character beats use it as a
  first-frame KEYFRAME (locks her face); B-roll beats use it as an INGREDIENTS
  reference (keeps the same woman/world without forcing her into the frame).
- Per-beat TTS for B-roll narration (narrator voice from manifest).
- Wave scheduler holds <=5 concurrent video jobs (account limit).
Prompts are final in the manifest (built by build_100.py)."""
import json, os, time, math, urllib.request, urllib.error, subprocess
BASE="https://69labs.vip/api/v1"; KEY=os.environ["LABS69_API_KEY"]
ROOT=os.path.dirname(os.path.abspath(__file__)); VID=os.path.dirname(ROOT)
SRC=os.path.join(VID,"Source clips"); AUD=os.path.join(ROOT,"audio")
FFPROBE="/usr/local/bin/ffprobe"; MAX_INFLIGHT=5
os.makedirs(SRC,exist_ok=True); os.makedirs(AUD,exist_ok=True)
M=json.load(open(os.path.join(ROOT,"manifest.json")))
SP=os.path.join(ROOT,"state.json")
state=json.load(open(SP)) if os.path.exists(SP) else {"beats":{}}
def save(): json.dump(state,open(SP,"w"),indent=2)
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
REF=M["reference_photo_url"]
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
            b=e.read().decode()[:300]
            if e.code==429: time.sleep(8); continue
            return e.code,{"error":b}
        except Exception: time.sleep(4)
    return 0,{"error":"retries"}
def dur(p):
    o=subprocess.run([FFPROBE,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip()
    try:return float(o)
    except:return 0.0
V=M["narrator_voice"]
def tts(text,dest):
    body={"text":text,"voiceProvider":V["provider"],"voiceId":V["voiceId"],"modelId":V["modelId"]}
    if V.get("speed"): body["voiceSettings"]={"speed":float(V["speed"])}
    st,j=req("POST","/tts/generate",body)
    jid=j.get("id")
    if not jid: print("  TTS fail",j); return False
    for _ in range(50):
        time.sleep(3); st,s=req("GET",f"/tts/status/{jid}")
        if s.get("status")=="COMPLETED": break
        if s.get("status") in("FAILED","CENSORED"): print("  TTS",s.get("status")); return False
    r=urllib.request.Request(f"{BASE}/tts/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
    with urllib.request.urlopen(r,timeout=120) as resp,open(dest,"wb") as f: f.write(resp.read())
    return os.path.getsize(dest)>2000
def submit_video(prompt,muted,mode):
    body={"prompt":prompt,"model":M["video_model"],"aspectRatio":M["aspect"]}
    if mode!="text": body["imageUrls"]=[REF]; body["videoInputMode"]=mode
    if muted: body["mute"]=True
    st,j=req("POST","/videos/generate",body)
    return (j.get("id"),None) if j.get("id") else (None,j.get("error",j))
def dl_video(jid,dest):
    r=urllib.request.Request(f"{BASE}/videos/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
    with urllib.request.urlopen(r,timeout=180) as resp,open(dest,"wb") as f: f.write(resp.read())
    return os.path.getsize(dest)
CLIP=float(M.get("clip_len",8.0))
# Stage A: TTS for narrated beats (broll + hook)
print("== Stage A: TTS ==",flush=True)
for b in M["beats"]:
    s=state["beats"].setdefault(b["id"],{})
    if b["type"]=="character": s["n_clips"]=1; continue
    dest=os.path.join(AUD,f"{b['id']}.mp3")
    if s.get("tts_done") and os.path.exists(dest): continue
    print("  TTS",b["id"],flush=True)
    if tts(b["sentence"],dest):
        d=dur(dest); s.update(tts_done=True,narration=dest,narration_dur=d,n_clips=max(1,math.ceil((d-0.05)/CLIP))); save()
    else: print("   FAILED",b["id"])
save()
# build task list (skip beats flagged preseeded/hook)
tasks=[]
for b in M["beats"]:
    if b.get("manual"): continue   # e.g. the hook clip is generated separately
    s=state["beats"][b["id"]]; n=s.get("n_clips",1); jobs=s.setdefault("jobs",{})
    for ci in range(n):
        jd=jobs.setdefault(str(ci),{"status":"pending","job_id":None,"file":None})
        if jd.get("status")=="downloaded" and jd.get("file") and os.path.exists(jd["file"]): continue
        jd.update(status="pending",job_id=None); tasks.append((b,ci))
save()
print(f"== {len(tasks)} clips to generate ==",flush=True)
inflight={}; qi=0; deadline=time.time()+60*55
while (qi<len(tasks) or inflight) and time.time()<deadline:
    while len(inflight)<MAX_INFLIGHT and qi<len(tasks):
        b,ci=tasks[qi]; muted=(b["type"]!="character")
        mode="keyframes" if b["type"]=="character" else "text"
        prompt=b["prompt"]
        if b["type"]!="character" and ci>0:
            ANG=[" Shoot this from a noticeably different, lower and closer side angle with a slow gentle push-in.",
                 " Shoot this from a slightly higher three-quarter angle with a slow pan across the action."]
            prompt=b["prompt"]+ANG[(ci-1)%len(ANG)]
        jid,err=submit_video(prompt,muted,mode)
        if jid:
            state["beats"][b["id"]]["jobs"][str(ci)].update(status="submitted",job_id=jid)
            inflight[jid]=(b,ci); qi+=1
            print(f"  submit {b['id']}[{ci}] {jid[:8]} ({len(inflight)})",flush=True); save(); time.sleep(13)
        else:
            es=str(err)
            if "Concurrent" in es or "FORBIDDEN" in es: break
            print(f"  submit FAIL {b['id']}[{ci}] {es[:100]}",flush=True); time.sleep(10); break
    done=[]
    for jid,(b,ci) in list(inflight.items()):
        st,s=req("GET",f"/videos/status/{jid}"); status=s.get("status")
        if status=="COMPLETED":
            dest=os.path.join(SRC,f"{b['id']}_k{ci}.mp4")
            try: sz=dl_video(jid,dest)
            except Exception as e: print("  dl err",e); continue
            if sz>100*1024:
                state["beats"][b["id"]]["jobs"][str(ci)].update(status="downloaded",file=dest)
                print(f"  DONE {b['id']}[{ci}] {sz}b",flush=True)
            else:
                state["beats"][b["id"]]["jobs"][str(ci)].update(status="pending",job_id=None); tasks.append((b,ci))
            done.append(jid); save()
        elif status in ("FAILED","CANCELLED"):
            print(f"  {status} {b['id']}[{ci}] requeue",flush=True)
            state["beats"][b["id"]]["jobs"][str(ci)].update(status="pending",job_id=None); tasks.append((b,ci)); done.append(jid); save()
    for jid in done: inflight.pop(jid,None)
    if len(inflight)>=MAX_INFLIGHT or (qi>=len(tasks) and inflight): time.sleep(15)
tot=down=0
for b in M["beats"]:
    for ci,jd in state["beats"][b["id"]].get("jobs",{}).items():
        tot+=1; down+=(jd.get("status")=="downloaded")
print(f"== DONE {down}/{tot} ==",flush=True); save()
