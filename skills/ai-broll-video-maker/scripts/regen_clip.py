#!/usr/bin/env python3
"""regen_clip.py <project_dir> <beat_id> [--stronger] [--prompt "override"]
Regenerate ONE beat's Veo clip (used by the realism gate's retry loop) and
overwrite its source file in <project_dir>/Source clips/<beat_id>.mp4, updating
state.json. Generic B-roll -> text-to-video; character/TH -> keyframe from ref.
--stronger appends an escalating realism clause (use on retries)."""
import sys, os, json, time, urllib.request, urllib.error, subprocess
BASE="https://69labs.vip/api/v1"; KEY=os.environ["LABS69_API_KEY"]
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36"
PROJ=sys.argv[1]; BID=sys.argv[2]
STRONGER="--stronger" in sys.argv
OVERRIDE=None
if "--prompt" in sys.argv: OVERRIDE=sys.argv[sys.argv.index("--prompt")+1]
PF=os.path.join(PROJ,"Project files"); SRC=os.path.join(PROJ,"Source clips")
M=json.load(open(os.path.join(PF,"manifest.json"))); S=json.load(open(os.path.join(PF,"state.json")))
REF=M["reference_photo_url"]; beat=next(b for b in M["beats"] if b["id"]==BID)
REALISM=(" The footage must look like REAL un-edited phone video of a real physical scene: "
"true real-world textures and lighting, correct physics, solid stable objects, natural hands, "
"no AI smoothness, no warping, no morphing, no melting edges, no impossible motion, no plastic "
"sheen, no uncanny look. Plain, ordinary, believable, slightly imperfect amateur footage. There is "
"continuous subtle handheld camera motion and real movement in the scene throughout; the frame is "
"NEVER static or frozen.")
def req(method,path,body=None,t=60):
    data=json.dumps(body).encode() if body else None
    h={"Authorization":f"Bearer {KEY}","User-Agent":UA,"Accept":"application/json"}
    if data:h["Content-Type"]="application/json"
    r=urllib.request.Request(BASE+path,data=data,headers=h,method=method)
    for _ in range(5):
        try:
            with urllib.request.urlopen(r,timeout=t) as resp: return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(8); continue
            return {"error":e.read().decode()[:200]}
        except Exception: time.sleep(4)
    return {"error":"retries"}
prompt=OVERRIDE or beat["prompt"]
if STRONGER: prompt=prompt+REALISM
body={"prompt":prompt,"model":M["video_model"],"aspectRatio":M["aspect"]}
mode = "keyframes" if (beat["type"]=="character" or beat.get("broll_mode")=="character") else "text"
muted = beat["type"]!="character"
if muted: body["mute"]=True
if mode!="text": body["imageUrls"]=[REF]; body["videoInputMode"]=mode
j=req("POST","/videos/generate",body); jid=j.get("id")
if not jid: print("submit fail",j); sys.exit(1)
print("job",jid)
st=None
for _ in range(75):
    time.sleep(8); s=req("GET",f"/videos/status/{jid}"); st=s.get("status")
    if st=="COMPLETED": break
    if st in("FAILED","CANCELLED"): print("gen",st); sys.exit(2)
if st!="COMPLETED": print("timeout, last status",st); sys.exit(3)
dest=os.path.join(SRC,f"{BID}.mp4")
ok=False
for attempt in range(6):
    try:
        r=urllib.request.Request(f"{BASE}/videos/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
        with urllib.request.urlopen(r,timeout=180) as resp,open(dest,"wb") as f: f.write(resp.read())
        if os.path.getsize(dest)>100*1024: ok=True; break
    except Exception as e:
        print("dl retry",attempt,str(e)[:60]); time.sleep(6)
if not ok: print("download failed after retries"); sys.exit(4)
S["beats"].setdefault(BID,{})["job"]={"status":"downloaded","job_id":jid,"file":os.path.abspath(dest)}
json.dump(S,open(os.path.join(PF,"state.json"),"w"),indent=2)
print("REGEN OK",dest,os.path.getsize(dest))
