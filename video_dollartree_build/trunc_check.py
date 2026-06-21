#!/usr/bin/env python3
"""trunc_check.py <project_dir> — transcribe every veo-spoken clip (talking_head + image_split)
and flag speech problems against the scripted sentence. Checks BOTH ends + the audio track:
  - TRUNCATED: the END of the line is missing (tail words absent and coverage < 85%).
  - LEAD-IN GIBBERISH (v6.2): veo prepended hallucinated words before the line (transcript does not
    start on the script's first words) — e.g. "Once I'm through making Comfrey..., okay, I did...".
  - MUTED (v6.2): no audio STREAM at all (ffprobe), or no speech heard. A re-rolled TH came back silent.
Any of these => re-roll the clip, then re-run this gate (re-rolls must be re-gated)."""
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
def has_audio_stream(cf):
    # v6.2: a re-rolled TH can come back with NO audio stream (silent Candice). ffprobe must show audio.
    r=subprocess.run([K.FP,"-v","error","-select_streams","a","-show_entries","stream=codec_type",
        "-of","default=nw=1",cf],capture_output=True,text=True)
    return "audio" in r.stdout
flags=[]; muted=[]; leadin=[]
for b in M["beats"]:
    vm=b.get("visual_mode")
    if vm not in ("talking_head","image_split"): continue
    cf=S["beats"].get(b["id"],{}).get("clip")
    if not cf or not os.path.exists(cf): print("MISS",b["id"]); continue
    if not has_audio_stream(cf):
        muted.append(b["id"]); print(f"{b['id']:13} MUTED (no audio stream — re-roll)"); continue
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
    # v6.2: LEAD-IN gibberish — veo prepends hallucinated words before the line. The transcript should
    # START on one of the script's first two content words; unrelated words before it = re-roll.
    opening=[w for w in script if len(w)>1][:2]
    start_idx=next((i for i,w in enumerate(tr) if w in opening), 99)
    if start_idx>=2 and opening:
        leadin.append(b["id"])
        print(f"{b['id']:13} LEAD-IN GIBBERISH (real line starts at word {start_idx})")
        print(f"    script: {b['sentence']}")
        print(f"    heard : {heard}")
print(f"\nMUTED ({len(muted)}): {','.join(muted)}")
print(f"TRUNCATED ({len(flags)}): {','.join(flags)}")
print(f"LEAD-IN GIBBERISH ({len(leadin)}): {','.join(leadin)}")
json.dump({"truncated":flags,"muted":muted,"leadin":leadin},open("/tmp/dt_trunc.json","w"))
