#!/usr/bin/env python3
"""Gap-aware assembler (FORMAT v2).
- Talking-head beat -> one segment: its own native audio; first 1.2s trimmed
  (keyframe-morph ghost); normalized.
- Gap (>=1 consecutive B-roll beats) -> one segment: the gap's B-roll clips
  concatenated and trimmed/looped to the gap's single TTS duration; audio = gap TTS.
All segments rendered identical (1280x720, 24fps CFR, AAC 48k) so concat can't drift."""
import json, os, subprocess, tempfile
ROOT=os.path.dirname(os.path.abspath(__file__)); VID=os.path.dirname(ROOT)
AUD=os.path.join(ROOT,"audio"); SEG=os.path.join(ROOT,"segments"); os.makedirs(SEG,exist_ok=True)
FF="/usr/local/bin/ffmpeg"; FP="/usr/local/bin/ffprobe"
M=json.load(open(os.path.join(ROOT,"manifest.json"))); state=json.load(open(os.path.join(ROOT,"state.json")))
VF="scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=24,format=yuv420p"
ANORM="loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000"
TH_TRIM=1.2
def run(c):
    r=subprocess.run(c,capture_output=True,text=True)
    if r.returncode!=0: print("FFERR",r.stderr[-300:])
    return r.returncode==0
def dur(p):
    o=subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip()
    try:return float(o)
    except:return 0.0
def finalize(vsrc,asrc,D,out):
    return run([FF,"-y","-i",vsrc,"-i",asrc,"-filter_complex",
        f"[0:v]{VF},trim=0:{D:.3f},setpts=PTS-STARTPTS[v];[1:a]aresample=async=1:first_pts=0,apad,atrim=0:{D:.3f},asetpts=PTS-STARTPTS[a]",
        "-map","[v]","-map","[a]","-r","24","-vsync","cfr","-c:v","libx264","-preset","medium","-crf","20",
        "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","48000","-ac","2",out])
def clipfile(bid):
    f=state["beats"].get(bid,{}).get("job",{}).get("file")
    return f if f and os.path.exists(f) else None

segments=[]; beats=M["beats"]; i=0
while i<len(beats):
    b=beats[i]
    if b["type"]=="character":
        cf=clipfile(b["id"])
        if cf:
            seg=os.path.join(SEG,f"{b['id']}.mp4"); cd=dur(cf); D=max(1.0,cd-TH_TRIM)
            # trim first TH_TRIM secs of both streams, normalize audio
            ok=run([FF,"-y","-ss",f"{TH_TRIM}","-i",cf,"-vf",VF,"-r","24","-af",ANORM,
                "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
                "-c:a","aac","-b:a","160k","-ar","48000","-ac","2",seg])
            if ok: segments.append(seg); print(f"  TH {b['id']} {dur(seg):.1f}s")
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
            run([FF,"-y","-i",c,"-an","-ss","0.2","-vf",VF,"-r","24","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",pv]); parts.append(pv)
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
        ok=finalize(vsrc,gmp3,D,seg)
        if ok: segments.append(seg); print(f"  GAP {gid} {dur(seg):.1f}s ({len(clips)} clips)")
        for p in parts: os.path.exists(p) and os.remove(p)
        for x in [pool,os.path.join(SEG,f'g{gid}_loop.mp4')]:
            os.path.exists(x) and os.remove(x)

lf=os.path.join(ROOT,"final_list.txt")
open(lf,"w").write("".join(f"file '{s}'\n" for s in segments))
out=os.path.join(VID,f"{M['title']}.mp4")
run([FF,"-y","-f","concat","-safe","0","-i",lf,"-fflags","+genpts","-r","24","-vsync","cfr",
    "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
    "-ar","48000","-ac","2","-movflags","+faststart",out])
va=subprocess.run([FP,"-v","error","-select_streams","a:0","-show_entries","stream=duration","-of","default=nk=1:nw=1",out],capture_output=True,text=True).stdout.strip()
print("FINAL:",out,f"v={dur(out):.1f}s a={va}s")
