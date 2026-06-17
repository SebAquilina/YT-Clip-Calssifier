#!/usr/bin/env python3
"""regen_queue.py <proj> <beat[:promptfile]> ...
Regenerate a list of beats with concurrency-limit awareness: keeps <=MAXC jobs in
flight, retries on FORBIDDEN (concurrent limit) with backoff, polls each to COMPLETED,
downloads, and updates state.json. Seeds TH from the beat's chain scene anchor and
B-roll from its hands ref (identity-safe); optional per-beat prompt override file."""
import sys,os,json,time,urllib.request,urllib.error
BASE="https://69labs.vip/api/v1"; KEY=os.environ["LABS69_API_KEY"]
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
PROJ=sys.argv[1]; PF=os.path.join(PROJ,"Project files"); SRC=os.path.join(PROJ,"Source clips")
M=json.load(open(os.path.join(PF,"manifest.json")))
REF=M["reference_photo_url"]; MAXC=4
def req(method,path,body=None,t=90):
    data=json.dumps(body).encode() if body is not None else None
    h={"Authorization":f"Bearer {KEY}","User-Agent":UA,"Accept":"application/json"}
    if data:h["Content-Type"]="application/json"
    r=urllib.request.Request(BASE+path,data=data,headers=h,method=method)
    try:
        with urllib.request.urlopen(r,timeout=t) as resp: return resp.status,json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try: return e.code,json.loads(e.read())
        except: return e.code,{"error":"x"}
    except Exception as ex: return 0,{"error":str(ex)}
def beat(bid): return next(b for b in M["beats"] if b["id"]==bid)
def seed_for(bid):
    b=beat(bid)
    if b["type"]=="character":
        for c in M.get("chains",[]):
            if bid in c.get("beat_ids",[]): return c.get("seed_keyframe_url",REF)
        return REF
    return b.get("broll_ref", M.get("hands_ref_url",REF))
items=[]
for a in sys.argv[2:]:
    if ":" in a: bid,pf=a.split(":",1); prompt=open(pf).read().strip()
    else: bid,prompt=a,None
    items.append((bid,prompt))
def submit(bid,prompt):
    b=beat(bid); muted=b["type"]!="character"
    body={"prompt":prompt or b["prompt"],"model":M["video_model"],"aspectRatio":M["aspect"],"skipWatermarkRemoval":False,
          "imageUrls":[seed_for(bid)],"videoInputMode":"keyframes"}
    if muted: body["mute"]=True
    st,j=req("POST","/videos/generate",body); return j.get("id"),j
inflight={}; queue=list(items); done=[]
while queue or inflight:
    while queue and len(inflight)<MAXC:
        bid,prompt=queue[0]
        jid,j=submit(bid,prompt)
        if jid: inflight[jid]=bid; queue.pop(0); print(f"submit {bid} {jid[:8]} ({len(inflight)} inflight)",flush=True); time.sleep(15)
        elif any(k in str(j) for k in ("FORBIDDEN","Concurrent","TOO_MANY_REQUESTS","Too many")):
            print(f"  busy/limited, waiting ({bid})",flush=True); break   # retry later, never drop
        else: print(f"  FAIL submit {bid}: {str(j)[:120]}",flush=True); queue.pop(0)
    if not inflight and queue: time.sleep(20); continue
    time.sleep(10)
    for jid,bid in list(inflight.items()):
        st,s=req("GET",f"/videos/status/{jid}"); status=s.get("status")
        if status=="COMPLETED":
            dest=os.path.join(SRC,f"{bid}.mp4"); ok=False
            for _ in range(6):
                try:
                    r=urllib.request.Request(f"{BASE}/videos/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
                    with urllib.request.urlopen(r,timeout=180) as resp,open(dest,"wb") as f: f.write(resp.read())
                    if os.path.getsize(dest)>100000: ok=True; break
                except Exception as e: time.sleep(6)
            if ok:
                S=json.load(open(os.path.join(PF,"state.json")))
                S["beats"].setdefault(bid,{})["job"]={"status":"downloaded","job_id":jid,"file":os.path.abspath(dest)}
                json.dump(S,open(os.path.join(PF,"state.json"),"w"),indent=2)
                print(f"DONE {bid}",flush=True); done.append(bid)
            inflight.pop(jid,None)
        elif status in("FAILED","CANCELLED"):
            print(f"{status} {bid} -> requeue",flush=True); queue.append((bid,dict(items).get(bid))); inflight.pop(jid,None)
print("REGEN_QUEUE DONE:",done)
