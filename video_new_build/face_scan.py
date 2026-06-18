#!/usr/bin/env python3
"""face_scan.py <project_dir> [--thresh 0.45] [--low 0.35] [--frames 8] [--json out.json]

Quantitative wrong-face detector using ArcFace (insightface buffalo_l) embeddings.

Reference = centroid of KNOWN-CLEAN Candice images (the canonical reference photo +
the five scene anchors). For every source clip we sample N frames evenly across the
clip, detect the largest face in each, and cosine-compare its embedding to the
reference centroid. A clip is FLAGGED when:
  - best_sim  < THRESH   -> it is never clearly Candice (wrong person throughout), or
  - worst_sim < LOW      -> at least one confident face is clearly a different person
                            (mid-clip drift to an imposter).
B-roll clips with no face simply pass (hands-only); a confident NON-Candice face in
B-roll is flagged too. Prints a per-clip table + a sorted summary, and (optional) JSON
list of flagged ids for the regen step."""
import os, sys, json, glob, warnings
warnings.filterwarnings("ignore")
import numpy as np, cv2, subprocess
from insightface.app import FaceAnalysis

PROJ=sys.argv[1]
def argf(flag,default):
    return type(default)(sys.argv[sys.argv.index(flag)+1]) if flag in sys.argv else default
THRESH=argf("--thresh",0.45); LOW=argf("--low",0.35); NFR=argf("--frames",8)
JOUT=sys.argv[sys.argv.index("--json")+1] if "--json" in sys.argv else None
PF=os.path.join(PROJ,"Project files")
M=json.load(open(os.path.join(PF,"manifest.json"))); S=json.load(open(os.path.join(PF,"state.json")))
FP="/usr/local/bin/ffprobe"; FF="/usr/local/bin/ffmpeg"
ASSETS="/home/user/YT-Clip-Calssifier/video_ps_veo/assets"
REFIMG="/tmp/_ref_full.jpg"

app=FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
app.prepare(ctx_id=-1, det_size=(640,640))
def emb_of(img):
    if img is None: return None
    faces=app.get(img)
    if not faces: return None,0.0
    f=max(faces,key=lambda x:x.det_score)
    return f.normed_embedding, float(f.det_score)
# --- reference centroid from clean Candice images ---
refs=[REFIMG]+[os.path.join(ASSETS,a) for a in ("bench_anchor.png","kitchen_anchor.png","shelf_anchor.png","packing_anchor.png","window_anchor.png")]
ref_embs=[]
for r in refs:
    if not os.path.exists(r): continue
    e=emb_of(cv2.imread(r))
    if e and e[0] is not None: ref_embs.append(e[0])
assert ref_embs, "no reference faces!"
CENT=np.mean(ref_embs,axis=0); CENT=CENT/np.linalg.norm(CENT)
print(f"reference centroid from {len(ref_embs)} clean Candice images",flush=True)
def cos(e): return float(np.dot(e,CENT))
def dur(p):
    try: return float(subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip())
    except: return 8.0
def clipfile(bid):
    f=S["beats"].get(bid,{}).get("job",{}).get("file")
    return f if f and os.path.exists(f) else None

rows=[]; flagged=[]
for b in M["beats"]:
    cf=clipfile(b["id"])
    if not cf: continue
    d=dur(cf); sims=[]; dets=[]
    for k in range(NFR):
        t=d*(k+0.5)/NFR
        jpg=f"/tmp/_fs_{os.getpid()}.jpg"
        subprocess.run([FF,"-y","-ss",f"{t:.2f}","-i",cf,"-frames:v","1","-vf","scale=640:-1",jpg],capture_output=True)
        if not os.path.exists(jpg): continue
        img=cv2.imread(jpg); os.remove(jpg)
        r=emb_of(img)
        if not r or r[0] is None: continue
        e,ds=r
        if ds<0.55: continue                     # ignore low-confidence (profile/blur) detections
        sims.append(cos(e)); dets.append(ds)
    typ=b["type"]
    if not sims:
        rows.append((b["id"],typ,None,None,len(sims),"PASS-noface")); continue
    best=max(sims); worst=min(sims)
    verdict="PASS"
    if typ=="character":
        if best<THRESH: verdict="FLAG-wrongface"
        elif worst<LOW: verdict="FLAG-drift"
    else:  # broll: only flag a clearly-wrong confident face
        if worst<LOW and best<THRESH: verdict="FLAG-brollface"
    if verdict.startswith("FLAG"): flagged.append(b["id"])
    rows.append((b["id"],typ,round(best,3),round(worst,3),len(sims),verdict))

print(f"\n{'id':12} {'type':10} {'best':>6} {'worst':>6} {'nf':>3}  verdict")
for r in sorted(rows,key=lambda x:(x[2] if x[2] is not None else 1.0)):
    print(f"{r[0]:12} {r[1]:10} {str(r[2]):>6} {str(r[3]):>6} {r[4]:>3}  {r[5]}")
print(f"\nFLAGGED ({len(flagged)}): {','.join(flagged)}")
if JOUT: json.dump(flagged,open(JOUT,"w"))
