#!/usr/bin/env python3
"""Assemble the final video from generated clips + narration.
Per beat -> one normalized segment (1280x720, 24fps, h264, aac stereo 48k):
  - character beat: the clip with its own Veo audio (speech), 8s.
  - broll beat: available clips concatenated into a pool, looped if needed to
    cover the narration length, trimmed to exactly the narration, narration mp3
    as the audio track.
Then concat all segments in manifest order -> final MP4.
"""
import json, os, subprocess, tempfile
ROOT=os.path.dirname(os.path.abspath(__file__)); VID=os.path.dirname(ROOT)
SRC=os.path.join(VID,"Source clips"); AUD=os.path.join(ROOT,"audio")
SEG=os.path.join(ROOT,"segments"); os.makedirs(SEG,exist_ok=True)
FF="/usr/local/bin/ffmpeg"; FP="/usr/local/bin/ffprobe"
M=json.load(open(os.path.join(ROOT,"manifest.json")))
state=json.load(open(os.path.join(ROOT,"state.json")))
VF="scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=24,format=yuv420p"
ANORM="loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000"

def run(cmd):
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode!=0: print("FFERR:",r.stderr[-500:])
    return r.returncode==0
def dur(p):
    o=subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip()
    try:return float(o)
    except:return 0.0

segments=[]
for b in M["beats"]:
    bid=b["id"]; s=state["beats"][bid]; jobs=s.get("jobs",{})
    clips=[jobs[str(i)]["file"] for i in range(s.get("n_clips",1))
           if jobs.get(str(i),{}).get("file") and os.path.exists(jobs[str(i)]["file"])]
    if not clips: print("  !! no clips",bid); continue
    seg=os.path.join(SEG,f"{bid}.mp4")
    if b["type"]=="character":
        ok=run([FF,"-y","-i",clips[0],"-vf",VF,"-r","24","-af",ANORM,
            "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
            "-c:a","aac","-b:a","160k","-ac","2","-t","8",seg])
    else:
        narr=s["narration"]; D=dur(narr)+0.30
        # build a video-only pool from available clips
        parts=[]
        for i,c in enumerate(clips):
            pv=os.path.join(SEG,f"{bid}_p{i}.mp4")
            run([FF,"-y","-i",c,"-an","-ss","0.25","-vf",VF,"-r","24",
                 "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",pv])
            parts.append(pv)
        pool=os.path.join(SEG,f"{bid}_pool.mp4")
        with tempfile.NamedTemporaryFile("w",suffix=".txt",delete=False) as f:
            for p in parts: f.write(f"file '{p}'\n")
            listf=f.name
        run([FF,"-y","-f","concat","-safe","0","-i",listf,"-an","-c:v","libx264",
             "-preset","medium","-crf","20","-pix_fmt","yuv420p",pool]); os.remove(listf)
        poolL=dur(pool)
        tmpv=os.path.join(SEG,f"{bid}_v.mp4")
        if poolL < D-0.05:
            run([FF,"-y","-stream_loop","-1","-i",pool,"-an","-t",f"{D:.2f}",
                 "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-r","24",tmpv])
        else:
            run([FF,"-y","-i",pool,"-an","-t",f"{D:.2f}",
                 "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-r","24",tmpv])
        ok=run([FF,"-y","-i",tmpv,"-i",narr,"-af",ANORM,"-map","0:v:0","-map","1:a:0",
            "-t",f"{D:.2f}","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
            "-c:a","aac","-b:a","160k","-ac","2",seg])
        for p in parts+[pool,tmpv]:
            if os.path.exists(p): os.remove(p)
    if ok and os.path.exists(seg):
        segments.append(seg); print(f"  {bid}: {dur(seg):.1f}s ({len(clips)} clip(s))")

listf=os.path.join(ROOT,"final_list.txt")
with open(listf,"w") as f:
    for s in segments: f.write(f"file '{s}'\n")
out=os.path.join(VID,f"{M['title']}.mp4")
run([FF,"-y","-f","concat","-safe","0","-i",listf,"-c:v","libx264","-preset","medium",
    "-crf","20","-pix_fmt","yuv420p","-r","24","-c:a","aac","-b:a","160k","-ac","2",
    "-movflags","+faststart",out])
print("FINAL:",out, f"{dur(out):.1f}s" if os.path.exists(out) else "FAILED")
