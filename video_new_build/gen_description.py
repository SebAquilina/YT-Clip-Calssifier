#!/usr/bin/env python3
"""gen_description.py — build a YouTube description (with auto chapters) for a video.

Chapters come from the build script's "# ===== ACT ... =====" boundaries: each act's
first beat is timed by summing the assembled segment durations (accounting for the
per-boundary crossfades) plus the CTA splice offset, so the timestamps line up with
the delivered video. Output order (per user spec):
  1) one-sentence book CTA + link
  2) main description
  3) chapter timestamps
  4) more description
  5) hashtags
Usage: gen_description.py <project_dir> <build_script> <config_json> > description.txt
"""
import sys, os, json, re, subprocess
FP="/usr/local/bin/ffprobe"
PROJ=sys.argv[1]; BUILD=sys.argv[2]; CFG=json.load(open(sys.argv[3]))
PF=os.path.join(PROJ,"Project files"); SEG=os.path.join(PF,"segments")
M=json.load(open(os.path.join(PF,"manifest.json")))
beats=M["beats"]
chain_of={}
for ci,c in enumerate(M.get("chains",[])):
    for bid in c.get("beat_ids",[]): chain_of[bid]=ci
def dur(p):
    try: return float(subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip())
    except: return 0.0

# --- reconstruct assembler segment order ---
segs=[]  # (type, first_beat_idx, filename)
i=0
while i<len(beats):
    b=beats[i]
    if b["type"]=="character":
        segs.append(("th",i,os.path.join(SEG,f"{b['id']}.mp4"))); i+=1
    else:
        gid=str(b.get("gap_id")); start_i=i
        while i<len(beats) and beats[i]["type"]=="broll" and str(beats[i].get("gap_id"))==gid: i+=1
        segs.append(("gap",start_i,os.path.join(SEG,f"gap_{gid}.mp4")))
SCHEME=CFG.get("scheme","smooth"); XF_IN=0.12; XF_OUT=0.40
def xfade(a,b):
    if SCHEME=="uniform": return XF_OUT
    if a[0]=="th" and b[0]=="th":
        if chain_of.get(beats[a[1]]["id"])==chain_of.get(beats[b[1]]["id"]): return XF_IN
    return XF_OUT
# cumulative start time per segment
seg_start=[0.0]*len(segs); acc=0.0
durs=[dur(s[2]) for s in segs]
for k in range(len(segs)):
    if k==0: seg_start[k]=0.0
    else: seg_start[k]=seg_start[k-1]+durs[k-1]-xfade(segs[k-1],segs[k])
# beat_idx -> assembled start time (TH: own seg; broll: its gap seg)
beat_start={}
for k,s in enumerate(segs):
    if s[0]=="th": beat_start[s[1]]=seg_start[k]
    else:
        gid=str(beats[s[1]].get("gap_id"))
        for j,b in enumerate(beats):
            if b["type"]=="broll" and str(b.get("gap_id"))==gid: beat_start[j]=seg_start[k]
CUT=float(CFG["cut"]); CTA=float(CFG.get("cta_dur",15.6))
def final_time(idx):
    t=beat_start.get(idx,0.0)
    return t if t<CUT else t+CTA

# --- parse build script ACTs -> (title, original-beat-index) ---
acts=[]; cnt=0
for ln in open(BUILD):
    m=re.match(r"\s*#\s*=+\s*ACT\s+([0-9]+[a-z]?)\s+(.*?)\s*=+\s*$", ln)
    if m: acts.append([m.group(2).strip(), cnt])
    elif re.match(r"\s*(th|br)\(", ln): cnt+=1
# manifests may contain inserted split beats (id like 'b00s_th') not present in the build script;
# map each build-script (original) beat index to its position in the current manifest beats list.
orig_pos=[i for i,b in enumerate(beats) if not b["id"].endswith("s_th")]
def act_manifest_idx(oi): return orig_pos[oi] if oi < len(orig_pos) else (orig_pos[-1] if orig_pos else 0)
def clean(title):
    t=re.sub(r"\s*\([^)]*\)","",title).strip()   # drop dev parentheticals
    t=t.strip(" -—:;")
    low=t.lower()
    if "hook" in low or "mrbeast" in low: return "Intro"
    if "verdict" in low or "cta" in low or "recap" in low: return "Final takeaway"
    t=re.sub(r"^(the|a)\s+","",t,flags=re.I)
    return t[0].upper()+t[1:] if t else "Chapter"
# build chapter list (dedupe consecutive same titles, ensure ascending + >=10s apart)
chap=[]
for title,idx in acts:
    ts=final_time(act_manifest_idx(idx)); ct=clean(title)
    chap.append((ts,ct))
chap.sort(key=lambda x:x[0])
# force first chapter to 0:00, drop ones <10s after previous, drop dup titles
final_ch=[]
for ts,ct in chap:
    ts=max(0.0,ts)
    if not final_ch:
        final_ch.append((0.0,ct)); continue
    if ts-final_ch[-1][0]<10:
        continue
    if ct==final_ch[-1][1]: continue
    final_ch.append((ts,ct))
def mmss(t):
    t=int(round(t)); return f"{t//60}:{t%60:02d}"

# --- emit description ---
out=[]
out.append(CFG["cta_sentence"].rstrip()+" \U0001F517 https://candicescandles.com")
out.append("")
out.append(CFG["body"].strip())
out.append("")
out.append("⏱️ Chapters")
for ts,ct in final_ch:
    out.append(f"{mmss(ts)} {ct}")
out.append("")
out.append(CFG["more"].strip())
out.append("")
out.append(CFG["hashtags"].strip())
print("\n".join(out))
