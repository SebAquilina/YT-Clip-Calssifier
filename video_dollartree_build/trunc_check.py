#!/usr/bin/env python3
"""trunc_check.py <project_dir> — transcribe every veo-spoken clip (talking_head + image_split)
and flag any whose spoken audio is cut off relative to the scripted sentence.
Heuristic: compare the last 4 words of the script tail to the transcript tail; also flag if
the transcript covers < 80% of the script word-count (veo truncated the sentence at gen)."""
import sys, os, json, re, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import imgkit as K
from faster_whisper import WhisperModel
PROJ=sys.argv[1]; PF=os.path.join(PROJ,"Project files")
M=json.load(open(os.path.join(PF,"manifest.json"))); S=json.load(open(os.path.join(PF,"state.json")))
mdl=WhisperModel("base.en", device="cpu", compute_type="int8")
def norm(s): return re.sub(r"[^a-z0-9 ]","",s.lower()).split()
def transcribe(cf):
    wav="/tmp/_tc.wav"
    subprocess.run([K.FF,"-y","-i",cf,"-ar","16000","-ac","1",wav],capture_output=True)
    segs,_=mdl.transcribe(wav, language="en")
    return " ".join(s.text for s in segs).strip()
flags=[]
for b in M["beats"]:
    vm=b.get("visual_mode")
    if vm not in ("talking_head","image_split"): continue
    cf=S["beats"].get(b["id"],{}).get("clip")
    if not cf or not os.path.exists(cf): print("MISS",b["id"]); continue
    script=norm(b["sentence"]); tr=norm(transcribe(cf))
    cov=len(tr)/max(1,len(script))
    tail_ok = script[-3:]==tr[-3:] if len(tr)>=3 and len(script)>=3 else False
    bad = cov<0.80 or (not tail_ok and cov<0.95)
    mark="  <<< TRUNCATED" if bad else ""
    if bad: flags.append(b["id"])
    print(f"{b['id']:12} cov={cov:.2f} tail_ok={tail_ok}{mark}")
    if bad:
        print(f"    script tail: ...{' '.join(script[-6:])}")
        print(f"    heard  tail: ...{' '.join(tr[-6:])}")
print(f"\nTRUNCATED ({len(flags)}): {','.join(flags)}")
json.dump({"truncated":flags},open("/tmp/dt_trunc.json","w"))
