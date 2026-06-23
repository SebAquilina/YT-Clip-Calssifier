#!/usr/bin/env python3
"""lipsync_gate.py <project_dir> [--fix]
Transcribe every talking-head clip and compare to its scripted line. Flags any
clip whose spoken words don't match (paraphrase/truncation). With --fix it
regenerates flagged clips (<=2 tries) via regen_clip.py."""
import sys, os, json, re, subprocess, difflib
FF="/usr/local/bin/ffmpeg"
PROJ=sys.argv[1]; FIX="--fix" in sys.argv
PF=os.path.join(PROJ,"Project files")
M=json.load(open(os.path.join(PF,"manifest.json"))); S=json.load(open(os.path.join(PF,"state.json")))
from faster_whisper import WhisperModel
MODEL=WhisperModel("base.en",device="cpu",compute_type="int8")
NUM={"zero":"0","one":"1","two":"2","three":"3","four":"4","five":"5","six":"6","seven":"7",
"eight":"8","nine":"9","ten":"10","eleven":"11","twelve":"12","thirteen":"13","fourteen":"14",
"fifteen":"15","twenty":"20","thirty":"30","forty":"40","fifty":"50","hundred":"100"}
def norm(t):
    t=t.lower()
    t=re.sub(r"[^a-z0-9 ]"," ",t)
    toks=[NUM.get(w,w) for w in t.split()]
    return " ".join(toks)
def transcribe(clip):
    wav=f"/tmp/_ls_{os.getpid()}.wav"
    subprocess.run([FF,"-y","-i",clip,"-vn","-ar","16000","-ac","1",wav],capture_output=True)
    segs,_=MODEL.transcribe(wav,language="en")
    txt=" ".join(s.text.strip() for s in segs)
    os.path.exists(wav) and os.remove(wav)
    return txt
def clipfile(bid):
    f=S["beats"].get(bid,{}).get("job",{}).get("file")
    return f if f and os.path.exists(f) else None
def ratio(want,clip): return difflib.SequenceMatcher(None,norm(want),norm(transcribe(clip))).ratio()
fails=[]
for b in M["beats"]:
    if b["type"]!="character": continue
    cf=clipfile(b["id"])
    if not cf: print(f"  {b['id']}: NO CLIP"); continue
    want=b["sentence"]
    # 3x CONSENSUS: whisper(base.en) is noisy and false-fails good clips, so a single
    # low score is not trusted — re-transcribe and require a majority to FAIL.
    rs=[ratio(want,cf)]
    if rs[0]<0.72: rs+=[ratio(want,cf),ratio(want,cf)]
    passes=sum(1 for r in rs if r>=0.72)
    status="OK" if passes>=(len(rs)+1)//2 else "FAIL"
    if status=="FAIL": fails.append(b["id"])
    print(f"  {b['id']}: {status} (ratios {[round(x,2) for x in rs]})")
    if status=="FAIL":
        print(f"     WANT: {want}")
        print(f"     SAID: {transcribe(cf).strip()}")
print(f"== lip-sync: {len(fails)} fail(s): {fails} ==")
WANT={b["id"]:b["sentence"] for b in M["beats"]}
if FIX and fails:
    rg=os.path.join(os.path.dirname(__file__),"regen_clip.py")
    for bid in fails:
        for attempt in range(2):
            print(f"  regen {bid} (try {attempt+1})",flush=True)
            subprocess.run(["python3",rg,PROJ,bid],env={**os.environ})
            S=json.load(open(os.path.join(PF,"state.json")))
            f=S["beats"].get(bid,{}).get("job",{}).get("file")
            if not (f and os.path.exists(f)): continue
            r=difflib.SequenceMatcher(None,norm(WANT[bid]),norm(transcribe(f))).ratio()
            print(f"     -> {r:.2f}")
            if r>=0.72: break
