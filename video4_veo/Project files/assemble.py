#!/usr/bin/env python3
"""Assembler v2 — fixes A/V drift.
Every segment is rendered to IDENTICAL specs (1280x720, 24fps CFR, AAC 48k
stereo) and its audio is padded/trimmed to EXACTLY the video length, so the
concat demuxer cannot accumulate audio/video drift (the cause of talking-head
lip desync). Character beats keep their native Veo speech; B-roll/hook beats
play their clip pool under the narration mp3."""
import json, os, subprocess, tempfile
ROOT=os.path.dirname(os.path.abspath(__file__)); VID=os.path.dirname(ROOT)
SRC=os.path.join(VID,"Source clips"); AUD=os.path.join(ROOT,"audio")
SEG=os.path.join(ROOT,"segments"); os.makedirs(SEG,exist_ok=True)
FF="/usr/local/bin/ffmpeg"; FP="/usr/local/bin/ffprobe"
M=json.load(open(os.path.join(ROOT,"manifest.json"))); state=json.load(open(os.path.join(ROOT,"state.json")))
VF="scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=24,format=yuv420p"
def run(c):
    r=subprocess.run(c,capture_output=True,text=True)
    if r.returncode!=0: print("FFERR",r.stderr[-400:])
    return r.returncode==0
def dur(p):
    o=subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip()
    try:return float(o)
    except:return 0.0
def finalize(vsrc,asrc,D,out):
    # mux: video trimmed to D, audio resampled+padded to EXACTLY D, both CFR
    return run([FF,"-y","-i",vsrc,"-i",asrc,
        "-filter_complex",
        f"[0:v]{VF},trim=0:{D:.3f},setpts=PTS-STARTPTS[v];"
        f"[1:a]aresample=async=1:first_pts=0,apad,atrim=0:{D:.3f},asetpts=PTS-STARTPTS[a]",
        "-map","[v]","-map","[a]","-r","24","-vsync","cfr",
        "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","160k","-ar","48000","-ac","2",out])
segments=[]
for b in M["beats"]:
    bid=b["id"]; s=state["beats"][bid]; jobs=s.get("jobs",{})
    clips=[jobs[str(i)]["file"] for i in range(s.get("n_clips",1))
           if jobs.get(str(i),{}).get("file") and os.path.exists(jobs[str(i)]["file"])]
    if not clips: print("  !! no clips",bid); continue
    seg=os.path.join(SEG,f"{bid}.mp4")
    if b["type"]=="character":
        D=min(8.0,dur(clips[0]))
        ok=finalize(clips[0],clips[0],D,seg)   # native Veo audio, locked to its own video length
    else:
        narr=s["narration"]; D=dur(narr)+0.30
        parts=[]
        for i,c in enumerate(clips):
            pv=os.path.join(SEG,f"{bid}_p{i}.mp4")
            run([FF,"-y","-i",c,"-an","-ss","0.20","-vf",VF,"-r","24","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",pv]); parts.append(pv)
        pool=os.path.join(SEG,f"{bid}_pool.mp4")
        with tempfile.NamedTemporaryFile("w",suffix=".txt",delete=False) as f:
            for p in parts: f.write(f"file '{p}'\n")
            lf=f.name
        run([FF,"-y","-f","concat","-safe","0","-i",lf,"-an","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",pool]); os.remove(lf)
        vsrc=pool
        if dur(pool)<D-0.05:
            looped=os.path.join(SEG,f"{bid}_loop.mp4")
            run([FF,"-y","-stream_loop","-1","-i",pool,"-an","-t",f"{D+0.5:.2f}","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-r","24",looped]); vsrc=looped
        ok=finalize(vsrc,narr,D,seg)
        for p in parts+[pool]:
            if os.path.exists(p): os.remove(p)
        lp=os.path.join(SEG,f"{bid}_loop.mp4")
        if os.path.exists(lp): os.remove(lp)
    if ok and os.path.exists(seg):
        va=dur(seg); segments.append(seg); print(f"  {bid}: {va:.2f}s ({len(clips)} clip)")
lf=os.path.join(ROOT,"final_list.txt")
with open(lf,"w") as f:
    for s in segments: f.write(f"file '{s}'\n")
out=os.path.join(VID,f"{M['title']}.mp4")
run([FF,"-y","-f","concat","-safe","0","-i",lf,"-fflags","+genpts","-r","24","-vsync","cfr",
    "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
    "-c:a","aac","-b:a","160k","-ar","48000","-ac","2","-movflags","+faststart",out])
vt=dur(out)
va=subprocess.run([FP,"-v","error","-select_streams","a:0","-show_entries","stream=duration","-of","default=nk=1:nw=1",out],capture_output=True,text=True).stdout.strip()
print("FINAL:",out,f"v={vt:.2f}s a={va}s" if os.path.exists(out) else "FAILED")
