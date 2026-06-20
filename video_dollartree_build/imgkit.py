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
# canonical workbench reference (her bench) — hosted URL written here after refs_build.py; used as an
# img2img reference so every image/scene shares the SAME wooden workbench surface & lighting.
BENCH_REF=open("/tmp/bench_ref.txt").read().strip() if os.path.exists("/tmp/bench_ref.txt") else None
# runtime override: refs_build.py writes high-quality, hosted scene keyframes + candice ref here.
if os.path.exists("/tmp/scene_refs.json"):
    _o=json.load(open("/tmp/scene_refs.json")); SCENES.update(_o.get("scenes",{}))
    if _o.get("candice"): CANDICE_REF=_o["candice"]
    if _o.get("bench"): BENCH_REF=_o["bench"]
VOICE={"voiceCloneId":"2e2ea1c5-13fb-4747-91c8-b7f3fc0b9482","model":"speech-2.8-hd","speed":1.05,"language_boost":"en"}

# ---- prompt blocks ----
IDENTITY=("This is the EXACT SAME woman shown in the reference keyframe image — identical face, tortoiseshell "
"glasses, curly LIGHT silvery-grey hair, blue knit sweater and tan apron, white, mid-fifties. Do NOT change her "
"face, age or ethnicity. ")
TH_STRICT=("Exactly ONE person, natural blink and lip-sync, steady framing; she begins the first word immediately "
"with no inhale and speaks continuously, no big inhale at the end.")
# audio rule for any veo clip that carries sound (talking head): her voice + natural room tone ONLY.
NOMUSIC=("AUDIO: only her speaking voice and quiet natural room tone — absolutely NO background music, NO soundtrack, "
"NO score, NO musical sting or jingle of any kind.")
# physics rule for B-roll/come-to-life: nothing may appear or vanish.
NOSPAWN=("Every object is physically present and real from the very first frame and stays put the entire time — "
"NOTHING pops in, spawns, materializes, fades in, fades out, appears or disappears; no new item ever enters or "
"leaves; hands only move things already on the bench. Continuous, physically correct real motion throughout.")
NOTEXT=("CRITICAL ABSOLUTE RULE: ZERO text rendered over the video — no subtitles, captions, transcription, "
"semi-transparent words, caption bar, lower-thirds, REC dot, UI, timecode, watermark or logos. Pure photographic "
"footage; the only printed words allowed are small real product/jar labels. Do NOT add subtitles.")
WS=("the same lived-in home candle workshop: her rustic wooden workbench with glass candle jars, soy wax, amber "
"fragrance-oil bottles, a kitchen thermometer and a curing shelf of finished candles behind, soft natural window light.")
# iPhone-realism clause — the single most important anti-"fake/3D-render" knob. Deep focus, NOT shallow; no studio look.
IPHONE=("A casual everyday snapshot a normal person quickly took on their phone — NOT a professional or staged photo. "
"Deep focus with everything sharp front to back, wide ~26mm-equivalent lens, natural available window light only, "
"true-to-life slightly flat color, real texture with faint sensor grain. Framing is casual and a little imperfect — "
"slightly off-center or mildly tilted, the kind of quick unplanned shot someone takes without composing it, maybe a "
"little too much empty space or a cut-off edge. Absolutely NO background blur or bokeh, NO studio/ring/softbox lighting, "
"NO cinematic color grade, NO glossy stock-photo or 3D-render/CGI look. It must look like an ordinary phone photo off a "
"real person's camera roll, taken on a real wooden workbench.")
# B-roll is intentionally a notch ROUGHER than the stills so it reads as genuine handheld human footage.
PHONE=("rough casual handheld smartphone footage shot by a normal person — slightly lower fidelity, a little soft with a "
"touch of natural motion blur, faint grain and slightly uneven exposure, real handheld shake, deep focus, natural window "
"light, NO bokeh, NO cinematic grade, NOT polished or professional; photo-real and physically correct, nothing spawns or "
"vanishes, five fingers, continuous subtle motion, never frozen.")

def th_prompt(sentence, scene="bench", moved=False):
    s={"bench":"seated at her rustic wooden candle-workshop workbench","kitchen":"standing at her kitchen stove station",
       "shelf":"standing beside her curing shelf of finished candles","packing":"standing at her packing table",
       "window":"seated by a bright window at a small side table"}[scene]
    lead=(f"She has just moved and is now {s}, settling naturally into frame as she keeps talking. " if moved
          else f"She is {s}, looking straight at camera. ")
    return (f"Casual handheld iPhone vlog clip filmed on a real workbench. {IDENTITY}{lead}She speaks directly to camera "
    f"in a warm American accent, lips fully in sync, saying exactly: \"{sentence}\". {TH_STRICT} {NOMUSIC} {IPHONE} {NOTEXT} "
    f"Setting: {WS}")

def image_prompt(subject, shot="close-up"):
    # LITERAL still of the thing being said, as an iPhone snapshot on her real workbench; no text; no stray people/faces
    return (f"A casual {shot} iPhone photo of {subject}, on a real rustic wooden candle-workshop workbench in a lived-in "
    f"home workshop, a little honest clutter around it. {IPHONE} No people and no faces unless explicitly part of the "
    f"subject; no hands unless needed. {NOTEXT}")

def live_motion(motion):
    return (f"The still phone photo comes to life with subtle real motion: {motion}, and a slow gentle handheld camera "
    f"push-in. {IPHONE} {NOSPAWN} No people appear. {NOTEXT}")

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

def gen_image(prompt, dest, image_urls=None, tries=3, aspect="16:9"):
    # nano-banana-2 supports aspectRatio in {16:9, 1:1, 3:4, 4:3, 9:16}
    for _ in range(tries):
        body={"model":"nano-banana-2","aspectRatio":aspect,"prompt":prompt}
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
