#!/usr/bin/env python3
"""deep_gate.py <project_dir> — deterministic quality gates beyond face/text/truncation:
  COHERENCE: full transcript vs script similarity (catches gibberish, veo-added junk like "tat",
             and adjacent beats with duplicate/near-identical lines).
  ADJACENCY: runs of >=2 consecutive talking_head beats (should be broken with B-roll/VO), and
             split part-1 fragments that end mid-clause (comma/conjunction) -> unnatural pause.
  RATE:      words-per-second per veo-spoken clip; reports the median TH rate + outliers so the
             cloned-TTS speed can be matched to it.
One whisper(small.en) pass over all clips/audio. Writes /tmp/<tag>_deep.json."""
import sys, os, json, re, subprocess, difflib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import imgkit as K
from faster_whisper import WhisperModel
PROJ=sys.argv[1]; PF=os.path.join(PROJ,"Project files"); tag=os.path.basename(PROJ.rstrip("/"))
M=json.load(open(os.path.join(PF,"manifest.json"))); S=json.load(open(os.path.join(PF,"state.json")))
mdl=WhisperModel("small.en",device="cpu",compute_type="int8")
def norm(s): return re.sub(r"[^a-z0-9 ]"," ",s.lower()).split()
def sim(a,b): return difflib.SequenceMatcher(None,norm(a),norm(b)).ratio()
def speech_end(p):
    r=subprocess.run([K.FF,"-i",p,"-af","silencedetect=noise=-30dB:d=0.3","-f","null","-"],capture_output=True,text=True)
    st=[float(x) for x in re.findall(r'silence_start: ([0-9.]+)',r.stderr)]
    en=[float(x) for x in re.findall(r'silence_end: ([0-9.]+)',r.stderr)]
    d=K.dur(p)
    if st and ((not en) or en[-1]<st[-1] or en[-1]>=d-0.12): return st[-1]
    return d
def transcribe(p):
    w="/tmp/_dg.wav"
    if os.path.exists(w): os.remove(w)
    subprocess.run([K.FF,"-y","-i",p,"-ar","16000","-ac","1",w],capture_output=True)
    if not os.path.exists(w): return None
    segs,_=mdl.transcribe(w,language="en"); return " ".join(s.text for s in segs).strip()

coh=[]; rates=[]; rate_rows=[]
prev_script=None; prev_id=None
for b in M["beats"]:
    vm=b["visual_mode"]; e=S["beats"].get(b["id"],{})
    src = e.get("clip") if vm in ("talking_head","image_split") else e.get("audio")
    script = b.get("sentence") if vm in ("talking_head","image_split") else b.get("narration","")
    if not src or not os.path.exists(src): continue
    h=transcribe(src)
    if h is None:
        coh.append((b["id"],"MUTED",script,"")); continue
    s=sim(script,h)
    if s<0.62: coh.append((b["id"],f"LOWSIM {s:.2f}",script,h))
    # duplicate adjacent line
    if prev_script and sim(prev_script,script)>0.85:
        coh.append((b["id"],f"DUP of {prev_id}",script,prev_script))
    prev_script, prev_id = script, b["id"]
    # rate (words/sec over speech span)
    se=speech_end(src); nwords=len(norm(h))
    if se>0.5 and nwords>=3:
        wps=nwords/se; rate_rows.append((b["id"],vm,round(wps,2),round(se,1),nwords))
        if vm=="talking_head": rates.append(wps)

# adjacency: runs of >=2 consecutive TH
beats=M["beats"]; adj=[]
run=[]
for b in beats+[{"visual_mode":"_end","id":"_"}]:
    if b["visual_mode"]=="talking_head": run.append(b["id"])
    else:
        if len(run)>=2: adj.append(run[:])
        run=[]
# mid-clause split fragments (part-1 ending with comma/and/or/leaving etc.)
frag=[]
for b in beats:
    if b["visual_mode"] in ("talking_head","image_split"):
        s=(b.get("sentence") or "").strip()
        if re.search(r"(,|\band\b|\bor\b|\bbut\b|\bso\b|\bthe\b|\bof\b|leaving)$", s.rstrip(".!?").strip(), re.I):
            frag.append((b["id"],s))

import statistics
med=round(statistics.median(rates),2) if rates else 0
out={"coherence":[{"id":c[0],"flag":c[1]} for c in coh],
     "adjacent_th_runs":adj,
     "midclause_fragments":[f[0] for f in frag],
     "th_rate_median_wps":med,
     "rate_outliers":[r[0] for r in rate_rows if med and (r[2]<med*0.7 or r[2]>med*1.4)]}
json.dump(out,open(f"/tmp/{tag}_deep.json","w"),indent=2)
print("=== COHERENCE (gibberish/junk/dup/muted) ===")
for c in coh: print(f"  {c[0]:14} {c[1]}\n     script: {c[2][:70]}\n     heard : {c[3][:70]}")
print(f"\n=== ADJACENT TH RUNS (>=2 in a row -> break with broll/VO) ===")
for r in adj: print("  "+", ".join(r))
print(f"\n=== MID-CLAUSE FRAGMENTS (unnatural ending) ===")
for f in frag: print(f"  {f[0]}: ...{' '.join(f[1].split()[-5:])}")
print(f"\n=== SPEECH RATE: TH median {med} wps | outliers: {out['rate_outliers']}")
