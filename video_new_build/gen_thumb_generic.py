#!/usr/bin/env python3
"""gen_thumb_generic.py <out.png> "<prompt>"  — thumbnail via nano-banana-2 with the
Candice character reference fed in (gpt-image-2 fails with imageUrls)."""
import os,sys,time,json,urllib.request,urllib.error
BASE="https://69labs.vip/api/v1"; KEY=os.environ["LABS69_API_KEY"]
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
OUT=sys.argv[1]; PROMPT=sys.argv[2]
CHAR_REF=open("/tmp/raw_ref.txt").read().strip()
def req(method,path,body=None,t=60):
    data=json.dumps(body).encode() if body is not None else None
    h={"Authorization":f"Bearer {KEY}","User-Agent":UA,"Accept":"application/json"}
    if data:h["Content-Type"]="application/json"
    r=urllib.request.Request(BASE+path,data=data,headers=h,method=method)
    for _ in range(5):
        try:
            with urllib.request.urlopen(r,timeout=t) as resp: return resp.status,json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(8); continue
            return e.code,{"error":e.read().decode()[:200]}
        except Exception: time.sleep(4)
    return 0,{"error":"x"}
def make(model):
    for _ in range(3):
        st,j=req("POST","/images/generate",{"prompt":PROMPT,"model":model,"aspectRatio":"16:9","imageUrls":[CHAR_REF]})
        jid=j.get("id"); print(f"[{model}] submit",st,jid,'' if jid else j,flush=True)
        if not jid: time.sleep(8); continue
        s=None
        for _ in range(90):
            time.sleep(4); _,info=req("GET",f"/images/status/{jid}"); s=info.get("status")
            if s in("COMPLETED","FAILED","CENSORED"): break
        print(f"[{model}]",s,flush=True)
        if s=="COMPLETED":
            r=urllib.request.Request(f"{BASE}/images/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
            with urllib.request.urlopen(r,timeout=120) as resp,open(OUT,"wb") as f: f.write(resp.read())
            print("saved",OUT,os.path.getsize(OUT),flush=True); return True
    return False
if not (make("nano-banana-2") or make("gpt-image-2")):
    raise SystemExit("thumb failed")
