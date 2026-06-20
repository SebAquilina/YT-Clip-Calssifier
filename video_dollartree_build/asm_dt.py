#!/usr/bin/env python3
"""asm_dt.py <project_dir> [out.mp4] — assemble the image-visuals video.
Builds one 1280x720/24fps/AAC seg per beat by visual_mode, delogos the veo watermark,
then joins with per-boundary crossfades (0.12s between consecutive face beats, 0.25s else)."""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imgkit as K
FF=K.FF; FP=K.FP
PROJ=sys.argv[1]; PF=os.path.join(PROJ,"Project files"); SEG=os.path.join(PF,"segments"); os.makedirs(SEG,exist_ok=True)
M=json.load(open(os.path.join(PF,"manifest.json"))); S=json.load(open(os.path.join(PF,"state.json")))
OUT=sys.argv[2] if len(sys.argv)>2 else os.path.join(PROJ,f"{M['title']}.mp4")
DELOGO="delogo=x=1198:y=676:w=78:h=40"
# per-segment loudness leveling so Veo talking-head audio and cloned-TTS narration sit at the SAME
# perceived level BEFORE the crossfade join (a global master alone preserves the source-to-source gap).
NORM="loudnorm=I=-18:TP=-2:LRA=11"
ENC=["-r","24","-vsync","cfr","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","48000","-ac","2"]
def run(c):
    r=subprocess.run(c,capture_output=True,text=True)
    if r.returncode!=0: print("FFERR",r.stderr[-300:])
    return r.returncode==0
def e(bid): return S["beats"].get(bid,{})

segs=[]; modes=[]
for b in M["beats"]:
    bid=b["id"]; vm=b.get("visual_mode",b.get("type")); st=e(bid); seg=os.path.join(SEG,f"{bid}.mp4")
    if vm in ("talking_head","image_split") and not st.get("clip"): print("skip(no clip)",bid); continue
    if vm=="talking_head":
        cf=st["clip"]
        run([FF,"-y","-i",cf,"-vf",f"{DELOGO},scale=1280:720,fps=24","-af",NORM,*ENC,seg])
    elif vm=="image_split":
        cf=st["clip"]; img=st.get("image"); thside=b.get("split",{}).get("th_side","left"); thf=b.get("split",{}).get("th_frac",0.46)
        if not img: print("skip split(no image)",bid); continue
        wTH=int(1280*thf)//2*2; wIM=1280-wTH; D=K.dur(cf)
        thfc=f"[0:v]{DELOGO},scale=1280:720,crop={wTH}:720:(in_w-{wTH})/2:0[L]"
        # cover-fit the (now 1:1) image into the pane: scale-to-increase + center-crop, never squeeze
        imfc=(f"[1:v]scale={wIM*2}:1440:force_original_aspect_ratio=increase,crop={wIM*2}:1440,"
              f"zoompan=z='min(zoom+0.0005,1.10)':d={int(D*24)}:s={wIM}x720:fps=24,setsar=1[R]")
        order="[L][R]" if thside=="left" else "[R][L]"
        run([FF,"-y","-i",cf,"-loop","1","-i",img,"-filter_complex",
             f"{thfc};{imfc};{order}hstack=2,format=yuv420p[v]","-map","[v]","-map","0:a","-af",NORM,"-t",f"{D:.3f}",*ENC,seg])
    elif vm=="image_full":
        img=st.get("image"); aud=st.get("audio"); D=(st.get("adur") or 3.0)+0.3
        if not (img and aud): print("skip full",bid); continue
        kb=b.get("kenburns",{}); z="min(zoom+0.0006,1.12)" if kb.get("dir","in")=="in" else "if(lte(zoom,1.0),1.12,max(zoom-0.0006,1.0))"
        run([FF,"-y","-loop","1","-i",img,"-i",aud,"-filter_complex",
             f"[0:v]scale=2560:-1,zoompan=z='{z}':d={int(D*24)}:s=1280x720:fps=24,format=yuv420p[v];"
             f"[1:a]aresample=48000,{NORM},apad,atrim=0:{D:.3f},asetpts=PTS-STARTPTS[a]","-map","[v]","-map","[a]","-t",f"{D:.3f}",*ENC,seg])
    elif vm=="image_live":
        cf=st.get("clip"); aud=st.get("audio"); D=(st.get("adur") or 3.0)+0.3
        if not (cf and aud): print("skip live",bid); continue
        D=min(D,K.dur(cf))
        run([FF,"-y","-i",cf,"-i",aud,"-filter_complex",
             f"[0:v]{DELOGO},scale=1280:720,trim=0:{D:.3f},setpts=PTS-STARTPTS,fps=24[v];"
             f"[1:a]aresample=48000,{NORM},apad,atrim=0:{D:.3f},asetpts=PTS-STARTPTS[a]","-map","[v]","-map","[a]","-t",f"{D:.3f}",*ENC,seg])
    elif vm=="broll":
        cf=st.get("clip"); aud=st.get("audio"); D=(st.get("adur") or 3.0)+0.3
        if not (cf and aud): print("skip broll",bid); continue
        cd=K.dur(cf); vsrc=cf
        if cd<D-0.05:
            lp=os.path.join(SEG,f"{bid}_loop.mp4"); run([FF,"-y","-stream_loop","-1","-i",cf,"-an","-t",f"{D+0.5:.2f}",*[x for x in ENC if x not in("-c:a","aac","-b:a","160k","-ar","48000","-ac","2")],lp]); vsrc=lp
        run([FF,"-y","-i",vsrc,"-i",aud,"-filter_complex",
             f"[0:v]{DELOGO},scale=1280:720,trim=0:{D:.3f},setpts=PTS-STARTPTS,fps=24[v];"
             f"[1:a]aresample=48000,{NORM},apad,atrim=0:{D:.3f},asetpts=PTS-STARTPTS[a]","-map","[v]","-map","[a]","-t",f"{D:.3f}",*ENC,seg])
    else:
        print("unknown mode",vm,bid); continue
    if os.path.exists(seg): segs.append(seg); modes.append(vm); print(f"  seg {bid} {vm} {K.dur(seg):.1f}s",flush=True)

# per-boundary crossfade join
def xf(i):
    face={"talking_head","image_split"}
    return 0.12 if (modes[i-1] in face and modes[i] in face) else 0.25
if len(segs)>1:
    durs=[K.dur(s) for s in segs]; inp=[]
    for s in segs: inp+=["-i",s]
    fc=[]; vl="[0:v]"; al="[0:a]"; acc=durs[0]
    for k in range(1,len(segs)):
        d=xf(k); off=max(0.0,acc-d); nv=f"[v{k}]"; na=f"[a{k}]"
        fc.append(f"{vl}[{k}:v]xfade=transition=fade:duration={d:.3f}:offset={off:.3f}{nv}")
        fc.append(f"{al}[{k}:a]acrossfade=d={d:.3f}:c1=tri:c2=tri{na}")
        vl,al=nv,na; acc=acc+durs[k]-d
    ok=run([FF,"-y",*inp,"-filter_complex",";".join(fc),"-map",vl,"-map",al,*ENC,"-movflags","+faststart",OUT])
    if not ok:
        lf=os.path.join(PF,"list.txt"); open(lf,"w").write("".join(f"file '{s}'\n" for s in segs))
        run([FF,"-y","-f","concat","-safe","0","-i",lf,"-fflags","+genpts",*ENC,"-movflags","+faststart",OUT])
elif segs:
    run([FF,"-y","-i",segs[0],"-c","copy",OUT])
print(f"ASSEMBLED: {OUT} {K.dur(OUT):.1f}s ({len(segs)} segments)",flush=True)
