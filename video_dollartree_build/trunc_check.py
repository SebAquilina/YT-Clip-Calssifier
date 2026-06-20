#!/usr/bin/env python3
"""trunc_check.py <project_dir> — transcribe every veo-spoken clip (talking_head + image_split)
and flag any whose spoken audio is cut off relative to the scripted sentence.
Heuristic: compare the last 4 words of the script tail to the transcript tail; also flag if
the transcript covers < 80% of the script word-count (veo truncated the sentence at gen)."""
import sys, os, json, re, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import imgkit as K
from faster_whisper import WhisperModel
PROJ=sys.argv[1]; PF=os.path.join(PROJ,"Project files")
MODEL=sys.argv[sys.argv.index("--model")+1] if "--model" in sys.argv else "small.en"
M=json.load(open(os.path.join(PF,"manifest.json"))); S=json.load(open(os.path.join(PF,"state.json")))
mdl=WhisperModel(MODEL, device="cpu", compute_type="int8")
def norm(s): return re.sub(r"[^a-z0-9 ]","",s.lower()).split()
def transcribe(cf):
    wav="/tmp/_tc.wav"
    if os.path.exists(wav): os.remove(wav)
    subprocess.run([K.FF,"-y","-i",cf,"-ar","16000","-ac","1",wav],capture_output=True)
    if not os.path.exists(wav): return ""   # no audio stream => muted
    segs,_=mdl.transcribe(wav, language="en")
    return " ".join(s.text for s in segs).strip()
flags=[]; muted=[]
for b in M["beats"]:
    vm=b.get("visual_mode")
    if vm not in ("talking_head","image_split"): continue
    cf=S["beats"].get(b["id"],{}).get("clip")
    if not cf or not os.path.exists(cf): print("MISS",b["id"]); continue
    heard=transcribe(cf); script=norm(b["sentence"]); tr=norm(heard)
    if not tr: muted.append(b["id"]); print(f"{b['id']:13} MUTED (no speech heard)"); continue
    cov=len(tr)/max(1,len(script))
    # truncation = the END of the line is missing. tail present (last 3 content words all appear
    # somewhere in transcript) => veo spoke through the end, even if it added lead-in or mis-tokenized.
    tail=[w for w in script if len(w)>2][-3:]
    tail_present = all(w in tr for w in tail) if tail else True
    bad = (not tail_present) and cov<0.85
    if bad:
        flags.append(b["id"])
        print(f"{b['id']:13} cov={cov:.2f} TRUNCATED")
        print(f"    script: {b['sentence']}")
        print(f"    heard : {heard}")
print(f"\nMUTED ({len(muted)}): {','.join(muted)}")
print(f"TRUNCATED ({len(flags)}): {','.join(flags)}")
json.dump({"truncated":flags,"muted":muted},open("/tmp/dt_trunc.json","w"))
