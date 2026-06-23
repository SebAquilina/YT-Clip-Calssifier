#!/usr/bin/env python3
"""qc.py — clip quality-control utilities for the realism gate.

  qc.py contactsheet <clip.mp4> <out.jpg> [n]
      Extract n evenly-spaced frames and tile them into one contact sheet for a
      vision judge (the Agent tool) to assess realism frame-by-frame.

  qc.py freeze <clip.mp4>
      Use ffmpeg freezedetect to report frozen/static spans. Prints "FREEZE <sec>"
      for each frozen span >= 0.6s, else "OK". (Catches the freeze-frame problem.)

  qc.py firstsec <clip.mp4> <out.jpg>
      Tile the first ~1.2s of frames (for talking-head ghost/morph inspection).
"""
import sys, os, subprocess, tempfile, json
FF="/usr/local/bin/ffmpeg"; FP="/usr/local/bin/ffprobe"
def dur(p):
    o=subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip()
    try: return float(o)
    except: return 0.0
def grab(clip,t,out):
    subprocess.run([FF,"-y","-ss",f"{t:.2f}","-i",clip,"-frames:v","1","-vf","scale=480:-1",out],
                   capture_output=True)
def tile(frames,out,cols=3):
    from PIL import Image
    ims=[Image.open(f) for f in frames if os.path.exists(f)]
    if not ims: return False
    w,h=ims[0].size; rows=(len(ims)+cols-1)//cols
    sheet=Image.new("RGB",(w*cols,h*rows),(20,20,20))
    for i,im in enumerate(ims): sheet.paste(im,((i%cols)*w,(i//cols)*h))
    sheet.save(out,quality=88); return True
def contactsheet(clip,out,n=6):
    d=dur(clip);
    if d<=0: return False
    ts=[d*(k+0.5)/n for k in range(n)]
    tmp=[]
    for k,t in enumerate(ts):
        f=f"/tmp/_qc_{os.getpid()}_{k}.jpg"; grab(clip,t,f); tmp.append(f)
    ok=tile(tmp,out,cols=3)
    for f in tmp:
        os.path.exists(f) and os.remove(f)
    return ok
def firstsec(clip,out):
    ts=[0.1,0.35,0.6,0.85,1.1,1.35]; tmp=[]
    for k,t in enumerate(ts):
        f=f"/tmp/_qcf_{os.getpid()}_{k}.jpg"; grab(clip,t,f); tmp.append(f)
    ok=tile(tmp,out,cols=3)
    for f in tmp: os.path.exists(f) and os.remove(f)
    return ok
def freeze(clip):
    r=subprocess.run([FF,"-i",clip,"-vf","freezedetect=n=-50dB:d=0.6","-map","0:v:0","-f","null","-"],
                     capture_output=True,text=True)
    spans=[]
    for line in r.stderr.splitlines():
        if "freeze_duration" in line:
            try: spans.append(float(line.split("freeze_duration:")[1].strip()))
            except: pass
    if spans: print("FREEZE "+" ".join(f"{s:.2f}" for s in spans))
    else: print("OK")
    return spans

if __name__=="__main__":
    cmd=sys.argv[1]
    if cmd=="contactsheet": print("OK" if contactsheet(sys.argv[2],sys.argv[3],int(sys.argv[4]) if len(sys.argv)>4 else 6) else "FAIL")
    elif cmd=="firstsec": print("OK" if firstsec(sys.argv[2],sys.argv[3]) else "FAIL")
    elif cmd=="freeze": freeze(sys.argv[2])
    else: print("usage: qc.py contactsheet|firstsec|freeze ...")
