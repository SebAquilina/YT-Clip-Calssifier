#!/usr/bin/env python3
"""assemble_smooth.py [<Project files dir>]  — improved assembler for videos 3-5.

Same gap-aware / seam-aware / color-lock / LUFS-leveling pipeline as the v5.2
assembler, PLUS per-boundary transitions to fix same-scene talking-head joins:

  - WITHIN a scene (consecutive clips in the SAME chain, which are frame-chained so
    clip N's last frame == clip N+1's first frame): a tiny MICRO crossfade
    (~0.12s) over the matched seam frames. Long enough to hide the small pose/light
    jump veo leaves at the cut, short enough that it never looks like a dissolve.
  - At a SCENE CHANGE (different chain / scene rotation) or a GAP boundary: a normal
    crossfade (~0.4s) for a clean, smooth scene transition.

The old assembler applied one uniform crossfade to every join, so same-scene cuts
got a visible ghost/pulse. This differentiates them.
Env: XFADE_IN (default 0.12), XFADE_OUT (default 0.40)."""
import json, os, subprocess, tempfile, re, statistics, sys
ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv)>1 else os.path.dirname(os.path.abspath(__file__))
VID=os.path.dirname(ROOT)
AUD=os.path.join(ROOT,"audio"); SEG=os.path.join(ROOT,"segments"); os.makedirs(SEG,exist_ok=True)
FF="/usr/local/bin/ffmpeg"; FP="/usr/local/bin/ffprobe"
M=json.load(open(os.path.join(ROOT,"manifest.json"))); state=json.load(open(os.path.join(ROOT,"state.json")))
TARGET_LUFS=-20.0
XF_IN=float(os.environ.get("XFADE_IN","0.12"))    # same-scene micro crossfade
XF_OUT=float(os.environ.get("XFADE_OUT","0.40"))  # scene-change / gap crossfade
def run(c):
    r=subprocess.run(c,capture_output=True,text=True)
    if r.returncode!=0: print("FFERR",r.stderr[-300:])
    return r.returncode==0
def dur(p):
    o=subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip()
    try:return float(o)
    except:return 0.0
def clipfile(bid):
    f=state["beats"].get(bid,{}).get("job",{}).get("file")
    return f if f and os.path.exists(f) else None
def yuv_mean(clip):
    r=subprocess.run([FF,"-i",clip,"-vf","fps=1,signalstats,metadata=print","-f","null","-"],capture_output=True,text=True)
    g=lambda k:[float(x) for x in re.findall(rf"{k}=([0-9.]+)",r.stderr)]
    ys,us,vs=g("YAVG"),g("UAVG"),g("VAVG")
    m=lambda a:sum(a)/len(a) if a else None
    return m(ys),m(us),m(vs)
def lutyuv(dy,du,dv):
    cl=lambda d:max(-22.0,min(22.0,d))
    return f"lutyuv=y='clip(val+{cl(dy):.0f},0,255)':u='clip(val+{cl(du):.0f},0,255)':v='clip(val+{cl(dv):.0f},0,255)'"
def gain_lufs(src,s0=None,e0=None):
    c=[FF]
    if s0 is not None: c+=["-ss",f"{s0:.2f}","-to",f"{e0:.2f}"]
    c+=["-i",src,"-af","loudnorm=I=-20:print_format=json","-f","null","-"]
    r=subprocess.run(c,capture_output=True,text=True)
    mt=re.search(r'"input_i"\s*:\s*"?(-?[0-9.]+)"?',r.stderr)
    if not mt: return 0.0
    try:
        ii=float(mt.group(1))
        if ii<=-70: return 0.0
        return max(-15.0,min(15.0,TARGET_LUFS-ii))
    except: return 0.0
def speech_bounds(clip):
    d=dur(clip)
    r=subprocess.run([FF,"-i",clip,"-af","silencedetect=n=-30dB:d=0.18","-f","null","-"],capture_output=True,text=True)
    starts=[]; ends=[]
    for ln in r.stderr.splitlines():
        if "silence_start:" in ln:
            try: starts.append(float(ln.split("silence_start:")[1].strip()))
            except: pass
        if "silence_end:" in ln:
            try: ends.append(float(ln.split("silence_end:")[1].split("|")[0].strip()))
            except: pass
    s0=0.0
    for st,en in zip(starts,ends):
        if st<=0.12: s0=max(s0,en)
    e0=d
    if len(starts)>len(ends): e0=min(e0,starts[-1])
    elif starts and starts[-1]>d-1.6 and (not ends or ends[-1]<=starts[-1]): e0=min(e0,starts[-1])
    s0=max(0.0,s0-0.04); e0=min(d,e0+0.12)
    if e0-s0<1.0: return 0.0,d
    return s0,e0

beats=M["beats"]
chain_start=set(); chain_end=set(); chain_of={}
for ci,c in enumerate(M.get("chains",[])):
    if c["beat_ids"]:
        chain_start.add(c["beat_ids"][0]); chain_end.add(c["beat_ids"][-1])
        for bid in c["beat_ids"]: chain_of[bid]=ci
print("color pre-pass...",flush=True)
yall=[];uall=[];vall=[]; cmean={}
allfiles=[clipfile(b["id"]) for b in beats]
for f in allfiles:
    if not f: continue
    y,u,v=yuv_mean(f)
    if y is None: continue
    cmean[f]=(y,u,v); yall.append(y);uall.append(u);vall.append(v)
TY,TU,TV=(statistics.median(yall),statistics.median(uall),statistics.median(vall)) if yall else (116,118,137)
print(f"  color target Y={TY:.0f} U={TU:.0f} V={TV:.0f} over {len(cmean)} clips",flush=True)
def vfilter(cf):
    y,u,v=cmean.get(cf,(TY,TU,TV))
    return f"{lutyuv(TY-y,TU-u,TV-v)},fps=24,format=yuv420p"

segments=[]; seg_scene=[]   # seg_scene[k] = ("th",chain_id) or ("gap",gid)
i=0
while i<len(beats):
    b=beats[i]
    if b["type"]=="character":
        cf=clipfile(b["id"])
        if cf:
            seg=os.path.join(SEG,f"{b['id']}.mp4")
            s0,e0=speech_bounds(cf)
            if b["id"] not in chain_start: s0=0.0
            if b["id"] not in chain_end:   e0=dur(cf)
            D=e0-s0; g=gain_lufs(cf,s0,e0); VF=vfilter(cf)
            ok=run([FF,"-y","-ss",f"{s0:.2f}","-to",f"{e0:.2f}","-i",cf,"-filter_complex",
                f"[0:v]{VF},trim=0:{D:.3f},setpts=PTS-STARTPTS[v];"
                f"[0:a]volume={g:.1f}dB,aresample=async=1:first_pts=0:osr=48000,apad,atrim=0:{D:.3f},asetpts=PTS-STARTPTS[a]",
                "-map","[v]","-map","[a]","-r","24","-vsync","cfr","-c:v","libx264","-preset","medium","-crf","20",
                "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","48000","-ac","2",seg])
            if ok: segments.append(seg); seg_scene.append(("th",chain_of.get(b["id"]))); print(f"  TH {b['id']} ch{chain_of.get(b['id'])} {s0:.2f}-{e0:.2f} g{g:+.0f}dB -> {dur(seg):.1f}s",flush=True)
        i+=1
    else:
        gid=str(b.get("gap_id")); grp=[]
        while i<len(beats) and beats[i]["type"]=="broll" and str(beats[i].get("gap_id"))==gid:
            grp.append(beats[i]); i+=1
        gmp3=state["gaps"].get(gid,{}).get("file")
        if not (gmp3 and os.path.exists(gmp3)): print("  !! gap",gid,"no tts"); continue
        D=dur(gmp3)+0.25
        clips=[clipfile(x["id"]) for x in grp if clipfile(x["id"])]
        if not clips: print("  !! gap",gid,"no clips"); continue
        parts=[]
        for j,c in enumerate(clips):
            pv=os.path.join(SEG,f"g{gid}_{j}.mp4")
            run([FF,"-y","-i",c,"-an","-ss","0.2","-vf",vfilter(c),"-r","24","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",pv]); parts.append(pv)
        pool=os.path.join(SEG,f"g{gid}_pool.mp4")
        with tempfile.NamedTemporaryFile("w",suffix=".txt",delete=False) as f:
            for p in parts: f.write(f"file '{p}'\n")
            lf=f.name
        run([FF,"-y","-f","concat","-safe","0","-i",lf,"-an","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",pool]); os.remove(lf)
        vsrc=pool
        if dur(pool)<D-0.05:
            lp=os.path.join(SEG,f"g{gid}_loop.mp4")
            run([FF,"-y","-stream_loop","-1","-i",pool,"-an","-t",f"{D+0.5:.2f}","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-r","24",lp]); vsrc=lp
        seg=os.path.join(SEG,f"gap_{gid}.mp4")
        g=gain_lufs(gmp3)
        ok=run([FF,"-y","-i",vsrc,"-i",gmp3,"-filter_complex",
            f"[0:v]trim=0:{D:.3f},setpts=PTS-STARTPTS[v];"
            f"[1:a]volume={g:.1f}dB,aresample=async=1:first_pts=0:osr=48000,apad,atrim=0:{D:.3f},asetpts=PTS-STARTPTS[a]",
            "-map","[v]","-map","[a]","-r","24","-vsync","cfr","-c:v","libx264","-preset","medium","-crf","20",
            "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","48000","-ac","2",seg])
        if ok: segments.append(seg); seg_scene.append(("gap",gid)); print(f"  GAP {gid} g{g:+.0f}dB {dur(seg):.1f}s ({len(clips)} clips)",flush=True)
        for p in parts: os.path.exists(p) and os.remove(p)
        for x in [pool,os.path.join(SEG,f'g{gid}_loop.mp4')]:
            os.path.exists(x) and os.remove(x)

# per-boundary transition durations
def bnd_dur(k):
    a,b=seg_scene[k-1],seg_scene[k]
    if a[0]=="th" and b[0]=="th" and a[1]==b[1] and a[1] is not None:
        return XF_IN          # same scene/chain -> micro crossfade over matched seam
    return XF_OUT             # scene change or gap boundary -> normal crossfade

out=os.path.join(VID,f"{M['title']}.mp4")
if len(segments)>1:
    durs=[dur(s) for s in segments]
    inp=[]
    for s in segments: inp+=["-i",s]
    fc=[]; vlab="[0:v]"; alab="[0:a]"; acc=durs[0]
    for k in range(1,len(segments)):
        xf=bnd_dur(k); off=max(0.0,acc-xf)
        nv=f"[v{k}]"; na=f"[a{k}]"
        fc.append(f"{vlab}[{k}:v]xfade=transition=fade:duration={xf:.3f}:offset={off:.3f}{nv}")
        fc.append(f"{alab}[{k}:a]acrossfade=d={xf:.3f}:c1=tri:c2=tri{na}")
        vlab,alab=nv,na; acc=acc+durs[k]-xf
    fcs=";".join(fc)
    ok=run([FF,"-y",*inp,"-filter_complex",fcs,"-map",vlab,"-map",alab,
        "-r","24","-vsync","cfr","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","160k","-ar","48000","-ac","2","-movflags","+faststart",out])
    if not ok:
        print("per-boundary xfade failed -> hard concat",flush=True)
        lf=os.path.join(ROOT,"final_list.txt"); open(lf,"w").write("".join(f"file '{s}'\n" for s in segments))
        run([FF,"-y","-f","concat","-safe","0","-i",lf,"-fflags","+genpts","-r","24","-vsync","cfr",
            "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
            "-ar","48000","-ac","2","-movflags","+faststart",out])
print("FINAL:",out,f"dur={dur(out):.1f}s  XF_IN={XF_IN} XF_OUT={XF_OUT}  segments={len(segments)}")
