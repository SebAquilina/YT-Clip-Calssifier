#!/usr/bin/env python3
"""finish_video.py <project_dir> <out.mp4> [--rounds 4] — gate -> auto-regen -> assemble -> master.

Each round: face scan (imposter), + one whisper pass that checks TH/split clips for truncation
(missing tail) / repetition (script-aware) / muted, and full/live/broll TTS for a truncated
narration. Offenders get their clip (or audio) popped and regenerated (gen_dt_par), with a per-beat
retry cap so a stubborn beat can't loop forever. Then assemble (asm_dt) + master_audio.
The no-text/caption VISION scan is NOT covered here — run that separately with an agent.
"""
import sys, os, json, re, subprocess
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); import imgkit as K
from faster_whisper import WhisperModel
PROJ=sys.argv[1]; OUT=sys.argv[2]
ROUNDS=int(sys.argv[sys.argv.index("--rounds")+1]) if "--rounds" in sys.argv else 4
PF=os.path.join(PROJ,"Project files"); SP=os.path.join(PF,"state.json")
M=json.load(open(os.path.join(PF,"manifest.json")))
tag=os.path.basename(PROJ.rstrip("/"))
mdl=WhisperModel("small.en",device="cpu",compute_type="int8")
def norm(s): return re.sub(r"[^a-z0-9 ]","",s.lower()).split()
def trig(w): return {tuple(w[i:i+3]) for i in range(len(w)-2)}
def transcribe(p):
    w="/tmp/_fv.wav"
    if os.path.exists(w): os.remove(w)
    subprocess.run([K.FF,"-y","-i",p,"-ar","16000","-ac","1",w],capture_output=True)
    if not os.path.exists(w): return None      # no audio = muted
    segs,_=mdl.transcribe(w,language="en"); return " ".join(s.text for s in segs).strip()
def tail_ok(script,heard):
    sw,hw=norm(script),norm(heard); tail=[x for x in sw if len(x)>2][-3:]
    return all(x in hw for x in tail) if tail else True
def rep_bad(script,heard):
    sw,hw=norm(script),norm(heard); sg=trig(sw)
    for i in range(len(hw)-2):
        if hw[i]==hw[i+1]==hw[i+2]: return True
    seen={}
    for i in range(len(hw)-2):
        t=tuple(hw[i:i+3])
        if t in seen and i-seen[t]>=3 and t not in sg: return True
        seen[t]=i
    return len(hw)>1.6*max(1,len(sw))

attempts={}
def run(c): return subprocess.run(c,capture_output=True,text=True).returncode==0

for rd in range(ROUNDS):
    S=json.load(open(SP))
    # face scan (subprocess)
    fj=f"/tmp/{tag}_face.json"
    subprocess.run(["python3",os.path.join(HERE,"..","video_new_build","face_scan.py"),PROJ,"--json",fj],
                   capture_output=True,text=True)
    face=set(json.load(open(fj)).get("flagged",[])) if os.path.exists(fj) else set()
    pop_clip=set(face); pop_audio=set()
    # whisper pass
    for b in M["beats"]:
        vm=b["visual_mode"]; e=S["beats"].get(b["id"],{})
        if vm in ("talking_head","image_split"):
            cf=e.get("clip")
            if not cf or not os.path.exists(cf): continue
            h=transcribe(cf)
            if h is None: pop_clip.add(b["id"]); continue          # muted
            if (not tail_ok(b["sentence"],h)) or rep_bad(b["sentence"],h): pop_clip.add(b["id"])
        elif vm in ("image_full","image_live","broll"):
            au=e.get("audio")
            if not au or not os.path.exists(au): pop_audio.add(b["id"]); continue
            h=transcribe(au)
            if h is None or not tail_ok(b.get("narration",""),h): pop_audio.add(b["id"])
    # apply retry cap (>=3 attempts on a beat => give up, leave as-is)
    pop_clip={i for i in pop_clip if attempts.get(i,0)<3}
    pop_audio={i for i in pop_audio if attempts.get("a:"+i,0)<3}
    print(f"[round {rd}] face={len(face)} pop_clip={sorted(pop_clip)} pop_audio={sorted(pop_audio)}",flush=True)
    if not pop_clip and not pop_audio: print("CLEAN",flush=True); break
    for i in pop_clip: S["beats"].get(i,{}).pop("clip",None); attempts[i]=attempts.get(i,0)+1
    for i in pop_audio:
        S["beats"].get(i,{}).pop("audio",None); S["beats"].get(i,{}).pop("adur",None); attempts["a:"+i]=attempts.get("a:"+i,0)+1
    json.dump(S,open(SP,"w"),indent=2)
    subprocess.run(["python3",os.path.join(HERE,"gen_dt_par.py"),PROJ,"--vid","5","--img","7","--tts","2"],
                   env={**os.environ,"LABS69_API_KEY":open("/tmp/apikey.txt").read().strip()})

print("assembling...",flush=True)
subprocess.run(["python3",os.path.join(HERE,"asm_dt.py"),PROJ,OUT])
mastered=OUT.replace(".mp4","_mastered.mp4")
subprocess.run(["python3",os.path.join(HERE,"..","skills","ai-broll-video-maker","scripts","master_audio.py"),OUT,mastered])
print(f"FINISH DONE: {mastered}",flush=True)
