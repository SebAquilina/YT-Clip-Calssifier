#!/usr/bin/env python3
"""chapters_gen.py <project_dir> <build_script.py> "<hook chapter title>"  (v6.2)
Generate YouTube chapter timestamps from the FINAL assembled cut. Runtimes change whenever clips
are re-rolled or the narration speed changes, so chapters must be timed against the real segments,
never hand-set. Parses the build script's `# ===== SECTION =====` headers, counts beat-producing
calls (th/book/full/split/live/br) to find each section's first beat, then replays the assembler's
chunked-crossfade timing over Project files/segments to get each section's start time. Sub-sections
that land < 11s after the previous chapter are merged (YouTube needs >=10s spacing). Prints
`M:SS  Title`; splice into the description's `⏱️ Chapters` block. Verify the book CTA lands < 1:30.
"""
import json,os,subprocess,sys,re
FP="/usr/local/bin/ffprobe"
PROJ=sys.argv[1]; BUILD=sys.argv[2]; HOOK=sys.argv[3] if len(sys.argv)>3 else "Intro"
SEG=os.path.join(PROJ,"Project files","segments")
M=json.load(open(os.path.join(PROJ,"Project files","manifest.json"))); beats=M["beats"]
def dur(p):
    try: return float(subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip())
    except: return 0.0
FACE={"talking_head","image_split"}
files=[os.path.join(SEG,b["id"]+".mp4") for b in beats]; modes=[b["visual_mode"] for b in beats]
durs=[dur(f) for f in files]
CH=16
def xf(pm,cm,dp,dc):
    d=0.12 if (pm in FACE and cm in FACE) else 0.25
    return min(d,dc-0.05,dp-0.05) if dc>0.2 and dp>0.2 else 0.05
bsic=[0.0]*len(files); chof=[0]*len(files); cdur=[]; i=0; ci=0
while i<len(files):
    grp=list(range(i,min(i+CH,len(files)))); acc=0.0
    for j,k in enumerate(grp):
        chof[k]=ci
        if j==0: bsic[k]=0.0; acc=durs[k]
        else:
            d=xf(modes[k-1],modes[k],durs[k-1],durs[k]); bsic[k]=max(0.0,acc-d); acc=acc+durs[k]-d
    cdur.append(acc); i+=CH; ci+=1
cs=[0.0]*len(cdur); acc=0.0
for c in range(len(cdur)):
    if c==0: cs[c]=0.0; acc=cdur[0]
    else:
        d=min(0.25,cdur[c]-0.05,cdur[c-1]-0.05) if cdur[c]>0.2 and cdur[c-1]>0.2 else 0.05
        cs[c]=max(0.0,acc-d); acc=acc+cdur[c]-d
st=[cs[chof[k]]+bsic[k] for k in range(len(files))]
# parse build script: section header -> beat index of next beat call
BEATCALL=re.compile(r'^\s*(th|book|full|split|live|br)\(')
SECT=re.compile(r'^\s*#\s*=+\s*(.+?)\s*=+\s*$')
sections=[]; cnt=0
for ln in open(BUILD):
    m=SECT.match(ln)
    if m: sections.append((m.group(1).strip(), cnt))
    elif BEATCALL.match(ln): cnt+=1
def clean(t):
    t=re.sub(r'\([^)]*\)','',t).strip()
    if t.upper().startswith("HOOK"): return HOOK
    if "EBOOK CTA" in t.upper(): return "My ebook (free first chapter)"
    if t.upper().startswith("OUTRO"): return "Watch this next"
    t=re.sub(r'^TOPIC\s+\d+:\s*','',t,flags=re.I)
    t=re.sub(r'^VARIATION:\s*','',t,flags=re.I)
    t=t[0].upper()+t[1:].lower()
    return t
def mmss(t): t=int(round(t)); return f"{t//60}:{t%60:02d}"
out=[]
for title,bi in sections:
    if bi>=len(st): continue
    ts=st[bi]; ct=clean(title)
    if not out: out.append((0.0,ct)); continue
    if ts-out[-1][0]<11: continue   # merge tiny sections
    if ct==out[-1][1]: continue
    out.append((ts,ct))
for ts,ct in out: print(f"{mmss(ts)}  {ct}")
