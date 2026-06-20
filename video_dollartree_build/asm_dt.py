#!/usr/bin/env python3
"""asm_dt.py <project_dir> [out.mp4] — assemble the image-visuals video.
Builds one 1280x720/24fps/AAC seg per beat by visual_mode, then chunked crossfade-joins.

Fixes baked in:
  #1 lip-sync: level each segment with a pure VOLUME GAIN (sample-aligned, no timing shift) instead
     of dynamic loudnorm (whose lookahead delayed the audio and desynced the lips).
  #2 TTS cutoff: generous tail padding (adur+0.6) so the trailing crossfade overlaps SILENCE, never speech.
  #3 awkward TH silence: crop each TH/split segment to just after speech ends (silencedetect + 0.35s buffer).
  #7 split framing: center the TH crop on Candice's detected face so she is never half-cut.
"""
import sys, os, json, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imgkit as K
FF=K.FF; FP=K.FP
PROJ=sys.argv[1]; PF=os.path.join(PROJ,"Project files"); SEG=os.path.join(PF,"segments"); os.makedirs(SEG,exist_ok=True)
M=json.load(open(os.path.join(PF,"manifest.json"))); S=json.load(open(os.path.join(PF,"state.json")))
OUT=sys.argv[2] if len(sys.argv)>2 else os.path.join(PROJ,f"{M['title']}.mp4")
DELOGO="delogo=x=1198:y=676:w=78:h=40"
BOOK="/home/user/YT-Clip-Calssifier/assets/book_inset.png"   # real book cover for the CTA inset
TARGET=-19.0   # per-segment loudness target (dB LUFS) reached via fixed gain — no timing change
ENC=["-r","24","-vsync","cfr","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","48000","-ac","2"]
def run(c):
    r=subprocess.run(c,capture_output=True,text=True)
    if r.returncode!=0: print("FFERR",r.stderr[-300:])
    return r.returncode==0
def e(bid): return S["beats"].get(bid,{})

_meas={}
def audio_measure(path):
    """(gain_db, speech_end_sec) — integrated loudness for a fixed-gain level + trailing-silence start."""
    if path in _meas: return _meas[path]
    r=subprocess.run([FF,"-i",path,"-af","loudnorm=print_format=json,silencedetect=noise=-30dB:d=0.35","-f","null","-"],
                     capture_output=True,text=True); err=r.stderr
    m=re.search(r'"input_i"\s*:\s*"([-0-9.]+)"',err); lufs=float(m.group(1)) if m else TARGET
    gain=max(-12.0,min(12.0,TARGET-lufs))
    dur=K.dur(path); starts=[float(x) for x in re.findall(r'silence_start: ([0-9.]+)',err)]
    ends=[float(x) for x in re.findall(r'silence_end: ([0-9.]+)',err)]
    speech_end=dur
    if starts:
        ls=starts[-1]
        if (not ends) or ends[-1] < ls or ends[-1] >= dur-0.12:   # last silence runs to the clip end
            speech_end=ls
    _meas[path]=(gain,speech_end); return _meas[path]

_app=None
def face_cx(cf):
    """center-x of Candice's face in a 1280-wide frame (fallback 640)."""
    global _app
    import cv2
    if _app is None:
        import warnings; warnings.filterwarnings("ignore")
        from insightface.app import FaceAnalysis
        _app=FaceAnalysis(name="buffalo_l",providers=["CPUExecutionProvider"]); _app.prepare(ctx_id=-1,det_size=(640,640))
    d=K.dur(cf); jpg=f"/tmp/_fc_{os.getpid()}.jpg"
    subprocess.run([FF,"-y","-ss",f"{d*0.45:.2f}","-i",cf,"-frames:v","1","-vf","scale=1280:720",jpg],capture_output=True)
    img=cv2.imread(jpg)
    try: os.remove(jpg)
    except: pass
    if img is None: return 640.0
    faces=_app.get(img)
    if not faces: return 640.0
    f=max(faces,key=lambda x:x.det_score); x1,_,x2,_=f.bbox; return float((x1+x2)/2)

segs=[]; modes=[]
for b in M["beats"]:
    bid=b["id"]; vm=b.get("visual_mode",b.get("type")); st=e(bid); seg=os.path.join(SEG,f"{bid}.mp4")
    if vm in ("talking_head","image_split") and not st.get("clip"): print("skip(no clip)",bid); continue
    if vm=="talking_head":
        cf=st["clip"]; gain,spend=audio_measure(cf)
        D=min(K.dur(cf), spend+0.35)                       # crop trailing silence (#3)
        if b.get("book_cta") and os.path.exists(BOOK):
            # CTA: real book cover composited bottom-left (veo renders books poorly), white border, gentle fade
            fc=(f"[0:v]{DELOGO},scale=1280:720,fps=24[bg];"
                f"[1:v]scale=-1:300,pad=iw+8:ih+8:4:4:white,format=rgba,colorchannelmixer=aa=0.96[bk];"
                f"[bg][bk]overlay=40:H-h-46:enable='gte(t,0.5)'[v]")
            run([FF,"-y","-i",cf,"-i",BOOK,"-t",f"{D:.3f}","-filter_complex",fc,"-map","[v]","-map","0:a",
                 "-af",f"volume={gain:.2f}dB",*ENC,seg])
        else:
            run([FF,"-y","-i",cf,"-t",f"{D:.3f}","-vf",f"{DELOGO},scale=1280:720,fps=24",
                 "-af",f"volume={gain:.2f}dB",*ENC,seg])         # volume gain, no desync (#1)
    elif vm=="image_split":
        cf=st["clip"]; img=st.get("image"); thside=b.get("split",{}).get("th_side","left"); thf=b.get("split",{}).get("th_frac",0.46)
        if not img: print("skip split(no image)",bid); continue
        wTH=int(1280*thf)//2*2; wIM=1280-wTH
        gain,spend=audio_measure(cf); D=min(K.dur(cf), spend+0.35)
        cx=face_cx(cf); cropx=int(max(0,min(1280-wTH, cx-wTH/2)))//2*2   # center on face (#7)
        thfc=f"[0:v]{DELOGO},scale=1280:720,crop={wTH}:720:{cropx}:0[L]"
        imfc=(f"[1:v]scale={wIM*2}:1440:force_original_aspect_ratio=increase,crop={wIM*2}:1440,"
              f"zoompan=z='min(zoom+0.0005,1.10)':d={int(D*24)}:s={wIM}x720:fps=24,setsar=1[R]")
        order="[L][R]" if thside=="left" else "[R][L]"
        run([FF,"-y","-i",cf,"-loop","1","-i",img,"-t",f"{D:.3f}","-filter_complex",
             f"{thfc};{imfc};{order}hstack=2,format=yuv420p[v]","-map","[v]","-map","0:a",
             "-af",f"volume={gain:.2f}dB",*ENC,seg])
    elif vm=="image_full":
        img=st.get("image"); aud=st.get("audio")
        if not (img and aud): print("skip full",bid); continue
        gain,_=audio_measure(aud); D=(st.get("adur") or 3.0)+0.6     # more tail headroom (#2)
        kb=b.get("kenburns",{}); z="min(zoom+0.0006,1.12)" if kb.get("dir","in")=="in" else "if(lte(zoom,1.0),1.12,max(zoom-0.0006,1.0))"
        run([FF,"-y","-loop","1","-i",img,"-i",aud,"-filter_complex",
             f"[0:v]scale=2560:-1,zoompan=z='{z}':d={int(D*24)}:s=1280x720:fps=24,format=yuv420p[v];"
             f"[1:a]aresample=48000,volume={gain:.2f}dB,apad,atrim=0:{D:.3f},asetpts=PTS-STARTPTS[a]",
             "-map","[v]","-map","[a]","-t",f"{D:.3f}",*ENC,seg])
    elif vm=="image_live":
        cf=st.get("clip"); aud=st.get("audio")
        if not (cf and aud): print("skip live",bid); continue
        gain,_=audio_measure(aud); D=min((st.get("adur") or 3.0)+0.6, K.dur(cf))
        run([FF,"-y","-i",cf,"-i",aud,"-filter_complex",
             f"[0:v]{DELOGO},scale=1280:720,trim=0:{D:.3f},setpts=PTS-STARTPTS,fps=24[v];"
             f"[1:a]aresample=48000,volume={gain:.2f}dB,apad,atrim=0:{D:.3f},asetpts=PTS-STARTPTS[a]",
             "-map","[v]","-map","[a]","-t",f"{D:.3f}",*ENC,seg])
    elif vm=="broll":
        cf=st.get("clip"); aud=st.get("audio")
        if not (cf and aud): print("skip broll",bid); continue
        gain,_=audio_measure(aud); D=(st.get("adur") or 3.0)+0.6
        cd=K.dur(cf); vsrc=cf
        if cd<D-0.05:
            lp=os.path.join(SEG,f"{bid}_loop.mp4"); run([FF,"-y","-stream_loop","-1","-i",cf,"-an","-t",f"{D+0.5:.2f}",*[x for x in ENC if x not in("-c:a","aac","-b:a","160k","-ar","48000","-ac","2")],lp]); vsrc=lp
        run([FF,"-y","-i",vsrc,"-i",aud,"-filter_complex",
             f"[0:v]{DELOGO},scale=1280:720,trim=0:{D:.3f},setpts=PTS-STARTPTS,fps=24[v];"
             f"[1:a]aresample=48000,volume={gain:.2f}dB,apad,atrim=0:{D:.3f},asetpts=PTS-STARTPTS[a]",
             "-map","[v]","-map","[a]","-t",f"{D:.3f}",*ENC,seg])
    else:
        print("unknown mode",vm,bid); continue
    if os.path.exists(seg): segs.append(os.path.abspath(seg)); modes.append(vm); print(f"  seg {bid} {vm} {K.dur(seg):.1f}s",flush=True)

# ---- chunked crossfade join (single 178-input graph is too large for one ffmpeg call) ----
FACE={"talking_head","image_split"}
def join(files, fmodes, dst):
    if len(files)==1: return run([FF,"-y","-i",files[0],"-c","copy",dst])
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

if len(segs)>1:
    CH=16; chunks=[]; cmodes=[]; i=0; ci=0
    while i<len(segs):
        cf=os.path.join(SEG,f"_chunk{ci}.mp4")
        if not join(segs[i:i+CH],modes[i:i+CH],cf): print("chunk",ci,"FAILED"); sys.exit(1)
        chunks.append(os.path.abspath(cf)); cmodes.append(modes[i]); print(f"  chunk {ci}: {K.dur(cf):.1f}s",flush=True)
        i+=CH; ci+=1
    join(chunks,[None]*len(chunks),OUT)
elif segs:
    run([FF,"-y","-i",segs[0],"-c","copy",OUT])
print(f"ASSEMBLED: {OUT} {K.dur(OUT):.1f}s ({len(segs)} segments)",flush=True)
