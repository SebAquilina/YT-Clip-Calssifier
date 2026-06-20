#!/usr/bin/env python3
"""rep_check.py <project_dir> — detect veo TH/split clips that REPEAT phrases to fill the 8s
(e.g. "same same same", or saying the sentence twice). Flags: a 3-word sequence that appears 2+
times, OR heard word-count > 1.5x the script (padding by repetition). Uses small.en."""
import sys, os, json, re, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import imgkit as K
from faster_whisper import WhisperModel
PROJ=sys.argv[1]; PF=os.path.join(PROJ,"Project files")
M=json.load(open(os.path.join(PF,"manifest.json"))); S=json.load(open(os.path.join(PF,"state.json")))
mdl=WhisperModel("small.en", device="cpu", compute_type="int8")
def norm(s): return re.sub(r"[^a-z0-9 ]","",s.lower()).split()
def has_rep(words):
    # immediate word triple (a a a) or repeated trigram
    for i in range(len(words)-2):
        if words[i]==words[i+1]==words[i+2]: return f"word x3: {words[i]}"
    seen={}
    for i in range(len(words)-2):
        tg=tuple(words[i:i+3]);
        if tg in seen and i-seen[tg]>=3: return f"trigram repeat: {' '.join(tg)}"
        seen[tg]=i
    return None
flags=[]
for b in M["beats"]:
    if b.get("visual_mode") not in ("talking_head","image_split"): continue
    cf=S["beats"].get(b["id"],{}).get("clip")
    if not cf or not os.path.exists(cf): continue
    if os.path.exists("/tmp/_rp.wav"): os.remove("/tmp/_rp.wav")
    subprocess.run([K.FF,"-y","-i",cf,"-ar","16000","-ac","1","/tmp/_rp.wav"],capture_output=True)
    if not os.path.exists("/tmp/_rp.wav"): continue
    segs,_=mdl.transcribe("/tmp/_rp.wav",language="en"); heard=" ".join(s.text for s in segs).strip()
    hw=norm(heard); sw=norm(b["sentence"])
    rep=has_rep(hw); over = len(hw)>1.5*max(1,len(sw))
    if rep or over:
        flags.append(b["id"])
        print(f"{b['id']:13} {'REP:'+rep if rep else ''} {'OVER %.1fx'%(len(hw)/max(1,len(sw))) if over else ''}")
        print(f"    heard: {heard}")
print(f"\nREPEATED ({len(flags)}): {','.join(flags)}")
json.dump({"repeated":flags},open("/tmp/dt_rep.json","w"))
