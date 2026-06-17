#!/usr/bin/env python3
"""book_cta.py <out_segment.mp4>
Build a standardized ~10s BOOK CTA segment: the book-cover image (slow Ken Burns zoom)
+ Candice-clone voiceover, 1280x720 / 24fps / AAC 48k — same spec as assembler segments,
so it can be concatenated/spliced into any video. Voiceover uses the cloned 'candice'
voice so it matches the gap narration. Book link goes in the description (not on screen)."""
import os,sys,json,time,urllib.request,urllib.error,subprocess
BASE="https://69labs.vip/api/v1"; KEY=os.environ["LABS69_API_KEY"]
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
FF="/usr/local/bin/ffmpeg"; FP="/usr/local/bin/ffprobe"
OUT=sys.argv[1] if len(sys.argv)>1 else "/tmp/book_cta.mp4"
BOOK="/home/user/YT-Clip-Calssifier/assets/book_cover.jpg"
VC="6f906e1c-3bcd-404f-9f35-e16c76a98be1"
# CTA voiceover is tailored PER VIDEO (passed as arg 2); same book-cover visual every time.
DEFAULT=("Oh, and quick thing before we carry on. If you love making candles, I have put my whole method "
"into my e-book, The Three Dollar Luxury Candle. The link is right down in the description below. Okay, back to it.")
CTA=sys.argv[2] if len(sys.argv)>2 else DEFAULT
def req(method,path,body=None,t=90):
    data=json.dumps(body).encode() if body is not None else None
    h={"Authorization":f"Bearer {KEY}","User-Agent":UA,"Accept":"application/json"}
    if data:h["Content-Type"]="application/json"
    r=urllib.request.Request(BASE+path,data=data,headers=h,method=method)
    try:
        with urllib.request.urlopen(r,timeout=t) as resp: return resp.status,json.loads(resp.read())
    except urllib.error.HTTPError as e: return e.code,{"error":e.read().decode()[:200]}
    except Exception as ex: return 0,{"error":str(ex)}
def dur(p):
    o=subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip()
    try: return float(o)
    except: return 0.0
# 1) TTS (candice clone)
mp3="/tmp/book_cta_vo.mp3"
st,j=req("POST","/voice-clones/generate",{"voiceCloneId":VC,"text":CTA,"model":"speech-2.8-hd","speed":1.05,"language_boost":"en"})
jid=j.get("id"); assert jid,j
for _ in range(60):
    time.sleep(3); _,s=req("GET",f"/tts/status/{jid}")
    if s.get("status") in("COMPLETED","FAILED","CENSORED"): break
rr=urllib.request.Request(f"{BASE}/tts/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
with urllib.request.urlopen(rr,timeout=90) as resp,open(mp3,"wb") as f: f.write(resp.read())
D=dur(mp3)+0.4; print(f"CTA voiceover {D:.1f}s")
# 2) book-cover Ken Burns segment (slow zoom in), 1280x720 24fps, with the VO
#    zoompan over D seconds; scale up first to avoid jitter
fc=(f"[0:v]scale=2560:-1,zoompan=z='min(zoom+0.0006,1.12)':d={int(D*24)}:s=1280x720:fps=24,"
    f"format=yuv420p[v];[1:a]aresample=48000,apad,atrim=0:{D:.3f},asetpts=PTS-STARTPTS[a]")
ok=subprocess.run([FF,"-y","-loop","1","-i",BOOK,"-i",mp3,"-filter_complex",fc,"-map","[v]","-map","[a]",
    "-t",f"{D:.3f}","-r","24","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
    "-c:a","aac","-b:a","160k","-ar","48000","-ac","2",OUT],capture_output=True,text=True)
if ok.returncode!=0: print("ERR",ok.stderr[-400:]); sys.exit(1)
print("BOOK CTA SEGMENT:",OUT,f"{dur(OUT):.1f}s")
