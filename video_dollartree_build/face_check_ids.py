#!/usr/bin/env python3
"""face_check_ids.py <project_dir> <id1,id2,...> — fast 2-class imposter check on specific beats.
Same Candice-vs-imposter centroid logic as face_scan.py but only for the listed ids. Prints
PASS/FLAG per id; exits 1 if any flagged."""
import os, sys, json, glob, warnings
warnings.filterwarnings("ignore")
import numpy as np, cv2, subprocess
from insightface.app import FaceAnalysis
PROJ=sys.argv[1]; IDS=sys.argv[2].split(",")
PF=os.path.join(PROJ,"Project files"); S=json.load(open(os.path.join(PF,"state.json")))
M={b["id"]:b for b in json.load(open(os.path.join(PF,"manifest.json")))["beats"]}
FF="/usr/local/bin/ffmpeg"; FPp="/usr/local/bin/ffprobe"
ASSETS="/home/user/YT-Clip-Calssifier/video_ps_veo/assets"; REFIMG="/tmp/_ref_full.jpg"
app=FaceAnalysis(name="buffalo_l",providers=["CPUExecutionProvider"]); app.prepare(ctx_id=-1,det_size=(640,640))
def emb(img):
    if img is None: return None
    f=app.get(img)
    if not f: return None
    g=max(f,key=lambda x:x.det_score); return g.normed_embedding,float(g.det_score)
refs=[REFIMG]+[os.path.join(ASSETS,a) for a in ("bench_anchor.png","kitchen_anchor.png","shelf_anchor.png","packing_anchor.png","window_anchor.png")]
re_=[]
for r in refs:
    if os.path.exists(r):
        x=emb(cv2.imread(r))
        if x: re_.append(x[0])
CENT=np.mean(re_,axis=0); CENT/=np.linalg.norm(CENT)
IMPDIR=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","video_new_build","imposter_refs")
ie=[]
for p in sorted(glob.glob(os.path.join(IMPDIR,"*.jpg"))):
    x=emb(cv2.imread(p))
    if x and x[1]>=0.5: ie.append(x[0])
IMP=np.mean(ie,axis=0); IMP/=np.linalg.norm(IMP)
def dur(p):
    try: return float(subprocess.run([FPp,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip())
    except: return 8.0
bad=False
for bid in IDS:
    cf=S["beats"].get(bid,{}).get("clip")
    if not cf or not os.path.exists(cf): print(f"{bid}: NOCLIP"); bad=True; continue
    d=dur(cf); nimp=0; n=0
    for k in range(8):
        t=d*(k+0.5)/8; jpg=f"/tmp/_fci_{os.getpid()}.jpg"
        subprocess.run([FF,"-y","-ss",f"{t:.2f}","-i",cf,"-frames:v","1","-vf","scale=640:-1",jpg],capture_output=True)
        im=cv2.imread(jpg);
        try: os.remove(jpg)
        except: pass
        r=emb(im)
        if not r or r[1]<0.55: continue
        n+=1
        if float(np.dot(r[0],CENT))-float(np.dot(r[0],IMP))<-0.02: nimp+=1
    verdict="FLAG-imposter" if nimp>=4 else ("REVIEW" if nimp>=2 else "PASS")
    if verdict!="PASS": bad=True
    print(f"{bid}: {verdict} (imposter-leaning {nimp}/{n} frames)")
sys.exit(1 if bad else 0)
