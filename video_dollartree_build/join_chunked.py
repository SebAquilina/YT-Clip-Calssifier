#!/usr/bin/env python3
"""join_chunked.py <project_dir> <out.mp4> — robustly crossfade-join many pre-built segments.
The single-pass 178-input xfade graph is too large for one ffmpeg call, so we do it in two
levels: xfade within chunks of ~16 segments, then xfade the chunk files together. Each segment
is re-encoded at most twice. Per-boundary durations: 0.12s between consecutive face beats
(talking_head/image_split), 0.25s otherwise."""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import imgkit as K
FF=K.FF
PROJ=sys.argv[1]; OUT=sys.argv[2]; PF=os.path.join(PROJ,"Project files"); SEG=os.path.join(PF,"segments")
M=json.load(open(os.path.join(PF,"manifest.json"))); S=json.load(open(os.path.join(PF,"state.json")))
ENC=["-r","24","-vsync","cfr","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
     "-c:a","aac","-b:a","160k","-ar","48000","-ac","2"]
def run(c):
    r=subprocess.run(c,capture_output=True,text=True)
    if r.returncode!=0: print("FFERR",r.stderr[-500:]); return False
    return True
FACE={"talking_head","image_split"}
segs=[]; modes=[]
for b in M["beats"]:
    p=os.path.join(SEG,f"{b['id']}.mp4")
    if os.path.exists(p) and K.dur(p)>0.1: segs.append(os.path.abspath(p)); modes.append(b.get("visual_mode"))
print(f"joining {len(segs)} segments")
def xf(i): return 0.12 if (modes[i-1] in FACE and modes[i] in FACE) else 0.25

def join(files, fmodes, dst):
    """xfade-chain a list of segment files (with per-boundary durations from fmodes)."""
    if len(files)==1:
        return run([FF,"-y","-i",files[0],"-c","copy",dst])
    durs=[K.dur(f) for f in files]; inp=[]
    for f in files: inp+=["-i",f]
    fc=[]; vl="[0:v]"; al="[0:a]"; acc=durs[0]
    for k in range(1,len(files)):
        d=0.12 if (fmodes[k-1] in FACE and fmodes[k] in FACE) else 0.25
        d=min(d, durs[k]-0.05, durs[k-1]-0.05) if durs[k]>0.2 and durs[k-1]>0.2 else 0.05
        off=max(0.0,acc-d); nv=f"[v{k}]"; na=f"[a{k}]"
        fc.append(f"{vl}[{k}:v]xfade=transition=fade:duration={d:.3f}:offset={off:.3f}{nv}")
        fc.append(f"{al}[{k}:a]acrossfade=d={d:.3f}:c1=tri:c2=tri{na}")
        vl,al=nv,na; acc=acc+durs[k]-d
    return run([FF,"-y",*inp,"-filter_complex",";".join(fc),"-map",vl,"-map",al,*ENC,"-movflags","+faststart",dst])

# level 1: chunks of 16
CH=16; chunks=[]; cmodes=[]
i=0; ci=0
while i<len(segs):
    grp=segs[i:i+CH]; gm=modes[i:i+CH]
    cf=os.path.join(SEG,f"_chunk{ci}.mp4")
    if not join(grp,gm,cf): print("chunk",ci,"FAILED"); sys.exit(1)
    chunks.append(os.path.abspath(cf))
    cmodes.append(modes[i])  # mode at the chunk's leading boundary (approx; chunk joins use 0.25 default)
    print(f"  chunk {ci}: {len(grp)} segs -> {K.dur(cf):.1f}s",flush=True)
    i+=CH; ci+=1
# level 2: join chunks (use 0.25 crossfades between chunks)
if not join(chunks,[None]*len(chunks),OUT): print("final join FAILED"); sys.exit(1)
print(f"JOINED: {OUT} {K.dur(OUT):.1f}s from {len(segs)} segments ({len(chunks)} chunks)",flush=True)
