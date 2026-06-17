#!/usr/bin/env python3
"""Generate new reference images for Candice, seeded from her canonical reference photo:
  1. hands_ref  - close-up of HER hands in HER workspace (for consistent B-roll)
  2. kitchen_anchor - her at the kitchen/stove station, looking at camera (2nd TH scene)
  3. shelf_anchor   - her by the curing shelf, looking at camera (3rd TH scene)
Uses nano-banana-2 (image editing) with the reference photo as imageUrls for likeness."""
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
    except urllib.error.HTTPError as e: return e.code,{"error":e.read().decode()[:300]}
    except Exception as ex: return 0,{"error":str(ex)}
def gen(name,prompt):
    st,j=req("POST","/images/generate",{"model":"nano-banana-2","aspectRatio":"16:9","prompt":prompt,"imageUrls":[REF]})
    jid=j.get("id"); print(f"[{name}] submit {st} {jid} {'' if jid else j}")
    if not jid: return
    for _ in range(50):
        time.sleep(4); s,info=req("GET",f"/images/status/{jid}")
        if info.get("status") in("COMPLETED","FAILED","CENSORED"): break
    if info.get("status")!="COMPLETED": print(f"  {name} -> {info.get('status')}"); return
    rr=urllib.request.Request(f"{BASE}/images/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
    dest=os.path.join(OUT,f"{name}.png")
    with urllib.request.urlopen(rr,timeout=90) as resp,open(dest,"wb") as f: f.write(resp.read())
    print(f"  saved {dest} ({os.path.getsize(dest)} bytes)")

WS=("the same candle workshop kitchen as the reference: rustic wooden workbench, soy wax, "
    "amber fragrance-oil bottles, a kitchen thermometer, a small digital scale, glass candle jars, "
    "a stovetop pot, a curing shelf of finished candles, warm natural daylight.")

gen("hands_ref",
    "Photoreal close-up of ONLY the hands and forearms of the SAME mid-fifties woman from the reference "
    "image (same fair, naturally aged skin, no rings except a plain wedding band, short clean nails), "
    "wearing the rolled cuffs of her blue knit sweater and tan apron, hands resting and working on her "
    f"rustic wooden candle-workshop bench. {WS} No face in frame, eye-level POV as if she is looking down "
    "at her own hands. Natural daylight, amateur smartphone look, five fingers per hand, anatomically correct.")

gen("kitchen_anchor",
    "The SAME woman from the reference image (mid-fifties, tortoiseshell glasses, curly grey hair, blue "
    "knit sweater, tan apron), now standing at the KITCHEN STOVE / counter station of her workshop with a "
    "stovetop pot of melting wax and shelves behind her, turned toward the camera, mid-conversation, warm "
    f"and friendly, sharp and in focus. {WS} Casual handheld smartphone vlog framing, natural window light.")

gen("shelf_anchor",
    "The SAME woman from the reference image (mid-fifties, tortoiseshell glasses, curly grey hair, blue "
    "knit sweater, tan apron), now standing beside the CURING SHELF of finished candles, turned toward the "
    f"camera, mid-conversation, sharp and in focus. {WS} Casual handheld smartphone vlog framing, natural light.")
