#!/usr/bin/env python3
"""Thumbnail for '50 Failed Candle Batches' — user's exact prompt, Candice reference fed
(nano-banana-2; gpt-image-2 fails with imageUrls here)."""
import os,time,json,urllib.request,urllib.error
BASE="https://69labs.vip/api/v1"; KEY=os.environ["LABS69_API_KEY"]
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
OUT="/home/user/YT-Clip-Calssifier/video_fail_veo/thumbnail.png"
CHAR_REF=open("/tmp/raw_ref.txt").read().strip()
PROMPT='''A YouTube thumbnail in the style of a veteran candlemaker channel.

SUBJECT: The SAME woman from the reference image (mid-fifties, tortoiseshell glasses, curly grey hair, blue knit sweater, tan apron) as the candlemaker, holding a magnifying glass over a row of failed candles, looking directly at camera.
FOCAL OBJECT: a row of about 10 candles, each marked with a bold red X.
TEXT OVERLAY: "#1 MISTAKE" in bold block sans-serif, bright red, upper-right third.
COLOUR PALETTE: cream + harsh red + lab white.
ANNOTATIONS: a red X on each candle; a magnifying glass held over them.
BACKGROUND: a lab-style workshop bench with many candles.
COMPOSITION: Face 35%, focal object 35%, text overlay 30%.
LIGHTING: slightly under-lit with strong key light from upper-left, warm dramatic shadows.

DO NOT INCLUDE: extra hands, any text other than the "#1 MISTAKE" overlay, multiple people, watermarks, brand logos, distorted faces, perfectly clean studio backgrounds.

Aspect ratio: 16:9. Style: photorealistic with bold graphic overlays.'''
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
    for _ in range(2):
        st,j=req("POST","/images/generate",{"prompt":PROMPT,"model":model,"aspectRatio":"16:9","imageUrls":[CHAR_REF]})
        jid=j.get("id"); print(f"[{model}] submit",st,jid,'' if jid else j)
        if not jid: continue
        s=None
        for _ in range(80):
            time.sleep(4); _,info=req("GET",f"/images/status/{jid}"); s=info.get("status")
            if s in("COMPLETED","FAILED","CENSORED"): break
        print(f"[{model}]",s)
        if s=="COMPLETED":
            r=urllib.request.Request(f"{BASE}/images/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
            with urllib.request.urlopen(r,timeout=120) as resp,open(OUT,"wb") as f: f.write(resp.read())
            print("saved",OUT,os.path.getsize(OUT)); return True
    return False
if not (make("nano-banana-2") or make("gpt-image-2")):
    raise SystemExit("thumb failed")
