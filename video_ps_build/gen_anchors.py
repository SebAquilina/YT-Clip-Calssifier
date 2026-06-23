#!/usr/bin/env python3
"""Regenerate/extend Candice's reference anchor set (FORMAT v5.1) — PARALLEL submit.
All seeded from her reference photo. CLEAN (no signs/UI/REC/outline), labeled jars,
talking-head scenes show her ready to speak; overhead shots are top-down action.
Submits all jobs first, then polls — robust to a slow image backend."""
import os,json,time,urllib.request,urllib.error
BASE="https://69labs.vip/api/v1"; KEY=os.environ["LABS69_API_KEY"]
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
REF=open("/tmp/raw_ref.txt").read().strip()
OUT="/home/user/YT-Clip-Calssifier/video_ps_veo/assets"; os.makedirs(OUT,exist_ok=True)
def req(method,path,body=None,t=60):
    url=path if path.startswith("http") else BASE+path
    data=json.dumps(body).encode() if body is not None else None
    h={"Authorization":f"Bearer {KEY}","User-Agent":UA,"Accept":"application/json"}
    if data:h["Content-Type"]="application/json"
    r=urllib.request.Request(url,data=data,headers=h,method=method)
    try:
        with urllib.request.urlopen(r,timeout=t) as resp: return resp.status,json.loads(resp.read())
    except urllib.error.HTTPError as e: return e.code,{"error":e.read().decode()[:200]}
    except Exception as ex: return 0,{"error":str(ex)}
PERSON=("the EXACT same woman as the reference image: mid-fifties, tortoiseshell glasses, curly grey hair, "
"blue knit sweater, tan apron — same face and identity, no other person.")
CLEAN=("ABSOLUTELY NO on-screen graphics: no camera viewfinder, no recording indicator, no red REC dot, no "
"battery icon, no frame border or corner brackets, no timecode, no hanging wall signs or printed signs, no "
"text overlays or watermarks. Clean photographic image, full-bleed edge to edge, plain walls.")
WS="a lived-in home candle workshop with warm natural daylight."
LABELS=("Glass candle jars on the shelves and bench have small, tidy, legible printed labels with short real "
"words like \"Lavender\", \"Soy Wax\", \"Vanilla\".")
def speak(where):
    return (f"Photoreal portrait of {PERSON} {where}, turned toward the camera and looking straight at it, mouth "
    f"slightly open as if just about to speak, warm and friendly, sharp and in focus, eye-level casual handheld "
    f"framing. {LABELS} {CLEAN} Setting: {WS}")
def overhead(action):
    return (f"Photoreal top-down overhead shot looking straight down at the rustic wooden candle-workshop bench, "
    f"showing ONLY the hands and forearms of {PERSON} (fair naturally-aged skin, plain wedding band, blue sweater "
    f"cuffs, tan apron) as she {action}. No face in frame. {LABELS} {CLEAN} Setting: {WS}")
JOBS={
 "bench_anchor": speak("seated at her rustic wooden workbench with finished labeled candle jars, a pour pitcher and a wick trimmer in front of her"),
 "kitchen_anchor": speak("standing at her kitchen stove with a stainless pot of melting wax and a thermometer on the cooktop beside her"),
 "shelf_anchor": speak("standing beside her tall curing shelf filled with rows of finished labeled candles"),
 "packing_anchor": speak("standing at a packing and labeling table with kraft boxes, twine and finished labeled candles ready to ship"),
 "window_anchor": speak("seated by a bright window at a small side table with a couple of lit candles and a notebook"),
 "overhead_action": overhead("pours melted wax from the metal pitcher into an empty glass jar with a centered wick, a thermometer and amber oil bottle nearby"),
}
ids={}
for name,prompt in JOBS.items():
    st,j=req("POST","/images/generate",{"model":"nano-banana-2","aspectRatio":"16:9","prompt":prompt,"imageUrls":[REF]})
    ids[name]=j.get("id"); print(f"submit {name}: {st} {ids[name] or j}",flush=True); time.sleep(2)
done=set()
for _ in range(150):
    time.sleep(6)
    for name,jid in ids.items():
        if name in done or not jid: continue
        st,info=req("GET",f"/images/status/{jid}"); s=info.get("status")
        if s=="COMPLETED":
            rr=urllib.request.Request(f"{BASE}/images/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
            dest=os.path.join(OUT,f"{name}.png")
            with urllib.request.urlopen(rr,timeout=90) as resp,open(dest,"wb") as f: f.write(resp.read())
            print(f"saved {name} ({os.path.getsize(dest)} bytes)",flush=True); done.add(name)
        elif s in("FAILED","CENSORED"):
            print(f"{name} -> {s}",flush=True); done.add(name)
    if len(done)>=len([i for i in ids.values() if i]): break
print(f"DONE anchor set: {len(done)} finished")
