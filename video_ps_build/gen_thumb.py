#!/usr/bin/env python3
"""Generate the POOR SCENT THROW thumbnail via gpt-image-2 (user's exact prompt)."""
import os, time, json, urllib.request, urllib.error
BASE="https://69labs.vip/api/v1"; KEY=os.environ["LABS69_API_KEY"]
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
OUT="/home/user/YT-Clip-Calssifier/video_ps_veo/thumbnail.png"
PROMPT='''A YouTube thumbnail in the style of a veteran candlemaker channel.

SUBJECT: A middle-aged candlemaker in a workshop apron, hand stopping a fragrance bottle from pouring, looking directly at camera.
FOCAL OBJECT: fragrance oil being held back from wax.
TEXT OVERLAY: "STOP POURING!" in bold block sans-serif, bright red, upper-right third.
COLOUR PALETTE: Amber + red + cream.
ANNOTATIONS: Red X on the fragrance bottle.
BACKGROUND: workshop with multiple fragrance oils visible.
COMPOSITION: Face 35%, focal object 35%, text overlay 30%.
LIGHTING: Slightly under-lit with strong key light from upper-left, warm dramatic shadows.

DO NOT INCLUDE: extra hands, text other than the overlay, multiple people, watermarks, brand logos, distorted faces, perfectly clean studio backgrounds.

Aspect ratio: 16:9. Style: photorealistic with bold graphic overlays.'''
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
        except Exception as ex: time.sleep(4)
    return 0,{"error":"x"}
st,j=req("POST","/images/generate",{"prompt":PROMPT,"model":"gpt-image-2","aspectRatio":"16:9"})
jid=j.get("id"); print("submit",st,jid,j if not jid else "")
assert jid,j
for _ in range(80):
    time.sleep(4); st,s=req("GET",f"/images/status/{jid}")
    status=s.get("status");
    if status=="COMPLETED": break
    if status in ("FAILED","CENSORED"): raise SystemExit(f"image failed: {s}")
print("status",status)
r=urllib.request.Request(f"{BASE}/images/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
with urllib.request.urlopen(r,timeout=120) as resp,open(OUT,"wb") as f: f.write(resp.read())
print("saved",OUT,os.path.getsize(OUT),"bytes")
