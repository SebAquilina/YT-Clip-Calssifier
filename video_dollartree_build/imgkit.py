#!/usr/bin/env python3
"""imgkit.py — shared refs, prompt templates, and 69labs helpers for the image-visuals
video pipeline (talking-head + full-frame image + split-screen + come-to-life + hands B-roll).
Implements references/image-visuals.md."""
import os, json, time, subprocess, urllib.request, urllib.error
BASE="https://69labs.vip/api/v1"
KEY=os.environ.get("LABS69_API_KEY") or open("/tmp/apikey.txt").read().strip()
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
FF="/usr/local/bin/ffmpeg"; FP="/usr/local/bin/ffprobe"
RAW="https://raw.githubusercontent.com/SebAquilina/YT-Clip-Calssifier/claude/10-candle-hacks-video-xijwmv/video_ps_veo/assets"
CANDICE_REF=open("/tmp/raw_ref.txt").read().strip() if os.path.exists("/tmp/raw_ref.txt") else f"{RAW}/bench_anchor.png"
SCENES={"bench":f"{RAW}/bench_anchor.png","kitchen":f"{RAW}/kitchen_anchor.png","shelf":f"{RAW}/shelf_anchor.png",
        "packing":f"{RAW}/packing_anchor.png","window":f"{RAW}/window_anchor.png"}
HANDS=f"{RAW}/hands_ref.png"; OVERHEAD=f"{RAW}/overhead_action.png"
VOICE={"voiceCloneId":"6f906e1c-3bcd-404f-9f35-e16c76a98be1","model":"speech-2.8-hd","speed":1.05,"language_boost":"en"}

# ---- prompt blocks ----
IDENTITY=("This is the EXACT SAME woman shown in the reference keyframe image — identical face, tortoiseshell "
"glasses, curly LIGHT silvery-grey hair, blue knit sweater and tan apron, white, mid-fifties. Do NOT change her "
"face, age or ethnicity. ")
TH_STRICT=("Exactly ONE person, natural blink and lip-sync, steady framing; she begins the first word immediately "
"with no inhale and speaks continuously, no big inhale at the end.")
NOTEXT=("CRITICAL ABSOLUTE RULE: ZERO text rendered over the video — no subtitles, captions, transcription, "
"semi-transparent words, caption bar, lower-thirds, REC dot, UI, timecode, watermark or logos. Pure photographic "
"footage; the only printed words allowed are small real product/jar labels. Do NOT add subtitles.")
WS=("an ordinary lived-in home candle workshop: a worktable with glass candle jars, soy wax, amber fragrance-oil "
"bottles, a kitchen thermometer and a curing shelf of finished candles, natural daylight.")
PHONE=("casual amateur smartphone footage: handheld, slight natural shake, natural light, deep focus; photo-real and "
"physically correct, nothing spawns or vanishes, hands have five fingers, continuous subtle motion, never frozen.")

def th_prompt(sentence, scene="bench", moved=False):
    s={"bench":"seated at her rustic wooden candle-workshop workbench","kitchen":"standing at her kitchen stove station",
       "shelf":"standing beside her curing shelf of finished candles","packing":"standing at her packing table",
       "window":"seated by a bright window at a small side table"}[scene]
    lead=(f"She has just moved and is now {s}, settling naturally into frame as she keeps talking. " if moved
          else f"She is {s}, looking straight at camera. ")
    return (f"Photoreal casual handheld smartphone vlog clip. {IDENTITY}{lead}She speaks directly to camera in a warm "
    f"American accent, lips fully in sync, saying exactly: \"{sentence}\". {TH_STRICT} {NOTEXT} Setting: {WS}")

def image_prompt(subject, shot="close-up"):
    # LITERAL still of the thing being said; warm amateur workshop aesthetic; no text; no stray people/faces
    return (f"Photoreal {shot} image of {subject}. Warm natural daylight, lived-in home candle workshop or rustic "
    f"wooden bench, true real-world textures, honest shallow depth, slightly imperfect amateur look — NOT glossy "
    f"stock, not cinematic. No people and no faces unless explicitly part of the subject; no hands unless needed. "
    f"{NOTEXT} 16:9.")

def live_motion(motion):
    return (f"The still photo comes to life with subtle real motion: {motion}, and a slow gentle camera push-in. "
    f"Photoreal, physically correct; nothing morphs, melts or spawns; no people appear; {NOTEXT}")

# ---- 69labs API ----
def req(method, path, body=None, t=90):
    url=path if path.startswith("http") else BASE+path
    data=json.dumps(body).encode() if body is not None else None
    h={"Authorization":f"Bearer {KEY}","User-Agent":UA,"Accept":"application/json"}
    if data: h["Content-Type"]="application/json"
    r=urllib.request.Request(url,data=data,headers=h,method=method)
    try:
        with urllib.request.urlopen(r,timeout=t) as resp: return resp.status,json.loads(resp.read())
    except urllib.error.HTTPError as e: return e.code,{"error":e.read().decode()[:200]}
    except Exception as e: return 0,{"error":str(e)}

def curl_dl(path, dest, kind="videos"):
    for _ in range(8):
        subprocess.run(["curl","-sL","--retry","6","--retry-all-errors","-m","300",
            "-H",f"Authorization: Bearer {KEY}","-H",f"User-Agent: {UA}",
            f"{BASE}/{kind}/download/{path}","-o",dest],capture_output=True)
        if os.path.exists(dest) and os.path.getsize(dest)>20000:
            if kind!="videos": return True
            pr=subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",dest],capture_output=True,text=True)
            try:
                if float(pr.stdout.strip())>0.4: return True
            except: pass
        time.sleep(5)
    return False

def submit_video(prompt, image_urls=None, mode="keyframes", muted=False):
    body={"prompt":prompt,"model":"veo-video","aspectRatio":"16:9","skipWatermarkRemoval":False}
    if muted: body["mute"]=True
    if image_urls: body["imageUrls"]=image_urls; body["videoInputMode"]=mode
    for _ in range(40):
        st,j=req("POST","/videos/generate",body); jid=j.get("id")
        if jid: return jid
        if any(k in str(j.get("error","")) for k in ("Concurrent","FORBIDDEN","limit")): time.sleep(12); continue
        return None
    return None

def wait_video(jid, dest):
    for _ in range(160):
        time.sleep(6); _,s=req("GET",f"/videos/status/{jid}"); st=s.get("status")
        if st=="COMPLETED": return curl_dl(jid,dest,"videos")
        if st in("FAILED","CANCELLED","CENSORED"): return False
    return False

def gen_video(prompt, dest, image_urls=None, mode="keyframes", muted=False, tries=4):
    for _ in range(tries):
        jid=submit_video(prompt,image_urls,mode,muted)
        if jid and wait_video(jid,dest): return True
        time.sleep(6)
    return False

def gen_image(prompt, dest, image_urls=None, tries=3):
    for _ in range(tries):
        body={"model":"nano-banana-2","aspectRatio":"16:9","prompt":prompt}
        if image_urls: body["imageUrls"]=image_urls
        st,j=req("POST","/images/generate",body); jid=j.get("id")
        if not jid:
            if any(k in str(j.get("error","")) for k in ("Concurrent","limit","FORBIDDEN")): time.sleep(10); continue
            return False
        for _ in range(90):
            time.sleep(4); _,info=req("GET",f"/images/status/{jid}"); s=info.get("status")
            if s=="COMPLETED":
                if curl_dl(jid,dest,"images"): return True
                break
            if s in("FAILED","CENSORED"): break
        time.sleep(6)
    return False

def tts(text, dest):
    st,j=req("POST","/voice-clones/generate",{"voiceCloneId":VOICE["voiceCloneId"],"text":text,
        "model":VOICE["model"],"speed":VOICE["speed"],"language_boost":VOICE["language_boost"]})
    jid=j.get("id")
    if not jid: return False
    done=False
    for _ in range(120):
        time.sleep(3); _,s=req("GET",f"/tts/status/{jid}")
        if s.get("status")=="COMPLETED": done=True; break
        if s.get("status") in("FAILED","CENSORED"): return False
    if not done: return False
    try:
        r=urllib.request.Request(f"{BASE}/tts/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
        with urllib.request.urlopen(r,timeout=120) as resp,open(dest,"wb") as f: f.write(resp.read())
    except Exception: return False
    return os.path.getsize(dest)>2000

def dur(p):
    try: return float(subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip())
    except: return 0.0
