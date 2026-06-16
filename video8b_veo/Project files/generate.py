#!/usr/bin/env python3
"""Gap-aware generator (FORMAT v2). Talking heads = Veo keyframe, OWN audio (no TTS).
B-roll = generic (text-to-video, no character) or character (keyframe). TTS is made
ONCE PER GAP (m['gaps']), never per beat. Wave scheduler <=5 concurrent."""
import json, os, time, urllib.request, urllib.error, subprocess
BASE="https://69labs.vip/api/v1"; KEY=os.environ["LABS69_API_KEY"]
ROOT=os.path.dirname(os.path.abspath(__file__)); VID=os.path.dirname(ROOT)
SRC=os.path.join(VID,"Source clips"); AUD=os.path.join(ROOT,"audio")
FP="/usr/local/bin/ffprobe"; MAX=5
os.makedirs(SRC,exist_ok=True); os.makedirs(AUD,exist_ok=True)
M=json.load(open(os.path.join(ROOT,"manifest.json"))); SP=os.path.join(ROOT,"state.json")
state=json.load(open(SP)) if os.path.exists(SP) else {"beats":{},"gaps":{}}
state.setdefault("gaps",{})
def save(): json.dump(state,open(SP,"w"),indent=2)
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
REF=M["reference_photo_url"]; V=M["narrator_voice"]
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
    body={"text":text,"voiceProvider":V["provider"],"voiceId":V["voiceId"],"modelId":V["modelId"]}
    if V.get("speed"): body["voiceSettings"]={"speed":float(V["speed"])}
    st,j=req("POST","/tts/generate",body); jid=j.get("id")
    if not jid: print("  TTS fail",j); return False
    for _ in range(60):
        time.sleep(3); st,s=req("GET",f"/tts/status/{jid}")
        if s.get("status")=="COMPLETED": break
        if s.get("status") in("FAILED","CENSORED"): print("  TTS",s.get("status")); return False
    r=urllib.request.Request(f"{BASE}/tts/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
    with urllib.request.urlopen(r,timeout=120) as resp,open(dest,"wb") as f: f.write(resp.read())
    return os.path.getsize(dest)>2000
def submit(prompt,muted,mode):
    body={"prompt":prompt,"model":M["video_model"],"aspectRatio":M["aspect"]}
    if muted: body["mute"]=True
    if mode!="text": body["imageUrls"]=[REF]; body["videoInputMode"]=mode
    st,j=req("POST","/videos/generate",body)
    return (j.get("id"),None) if j.get("id") else (None,j.get("error",j))
def dl(jid,dest):
    r=urllib.request.Request(f"{BASE}/videos/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
    with urllib.request.urlopen(r,timeout=180) as resp,open(dest,"wb") as f: f.write(resp.read())
    return os.path.getsize(dest)

# Stage A: ONE TTS per gap
print("== Stage A: gap TTS (one per gap) ==",flush=True)
for gid,text in M["gaps"].items():
    g=state["gaps"].setdefault(gid,{})
    dest=os.path.join(AUD,f"gap_{gid}.mp3")
    if g.get("done") and os.path.exists(dest): continue
    print("  TTS gap",gid,flush=True)
    if tts(text,dest): g.update(done=True,file=dest,dur=dur(dest)); save()
    else: print("   FAILED gap",gid)
save()
# Stage B/C: video per beat
tasks=[]
for b in M["beats"]:
    s=state["beats"].setdefault(b["id"],{})
    jd=s.setdefault("job",{"status":"pending","job_id":None,"file":None})
    if jd.get("status")=="downloaded" and jd.get("file") and os.path.exists(jd["file"]): continue
    jd.update(status="pending",job_id=None); tasks.append(b)
save()
print(f"== {len(tasks)} video clips to generate ==",flush=True)
inflight={}; qi=0; deadline=time.time()+60*55
while (qi<len(tasks) or inflight) and time.time()<deadline:
    while len(inflight)<MAX and qi<len(tasks):
        b=tasks[qi]
        if b["type"]=="character": muted=False; mode="keyframes"
        elif b.get("broll_mode")=="character": muted=True; mode="keyframes"
        else: muted=True; mode="text"
        jid,err=submit(b["prompt"],muted,mode)
        if jid:
            state["beats"][b["id"]]["job"].update(status="submitted",job_id=jid); inflight[jid]=b; qi+=1
            print(f"  submit {b['id']} {jid[:8]} ({len(inflight)})",flush=True); save(); time.sleep(13)
        else:
            es=str(err)
            if "Concurrent" in es or "FORBIDDEN" in es: break
            print(f"  FAIL {b['id']} {es[:90]}",flush=True); time.sleep(10); break
    done=[]
    for jid,b in list(inflight.items()):
        st,s=req("GET",f"/videos/status/{jid}"); status=s.get("status")
        if status=="COMPLETED":
            dest=os.path.join(SRC,f"{b['id']}.mp4")
            try: sz=dl(jid,dest)
            except Exception as e: print("dl err",e); continue
            if sz>100*1024: state["beats"][b["id"]]["job"].update(status="downloaded",file=dest); print(f"  DONE {b['id']}",flush=True)
            else: state["beats"][b["id"]]["job"].update(status="pending",job_id=None); tasks.append(b)
            done.append(jid); save()
        elif status in ("FAILED","CANCELLED"):
            state["beats"][b["id"]]["job"].update(status="pending",job_id=None); tasks.append(b); done.append(jid)
            print(f"  {status} {b['id']} requeue",flush=True); save()
    for jid in done: inflight.pop(jid,None)
    if len(inflight)>=MAX or (qi>=len(tasks) and inflight): time.sleep(15)
down=sum(1 for b in M["beats"] if state["beats"][b["id"]]["job"].get("status")=="downloaded")
print(f"== DONE {down}/{len(M['beats'])} ==",flush=True); save()
