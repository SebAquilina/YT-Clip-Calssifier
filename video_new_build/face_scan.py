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
THRESH=argf("--thresh",0.44); LOW=argf("--low",0.35); NFR=argf("--frames",8)
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
# imposter centroid: the recurring wrong face (confirmed imposter frames committed in the repo).
# A single distance-to-Candice threshold cannot separate wide-shot Candice from the imposter
# (they overlap ~0.42-0.52); comparing distance-to-Candice vs distance-to-imposter does.
IMPDIR=os.path.join(os.path.dirname(os.path.abspath(__file__)),"imposter_refs")
imp_embs=[]
for p in sorted(glob.glob(os.path.join(IMPDIR,"*.jpg"))):
    e=emb_of(cv2.imread(p))
    if e and e[0] is not None and e[1]>=0.5: imp_embs.append(e[0])
IMP=np.mean(imp_embs,axis=0); IMP=IMP/np.linalg.norm(IMP) if imp_embs else None
print(f"candice centroid from {len(ref_embs)} clean images | imposter centroid from {len(imp_embs)} frames",flush=True)
def cos(e): return float(np.dot(e,CENT))
def cosi(e): return float(np.dot(e,IMP)) if IMP is not None else -1.0
def dur(p):
    try: return float(subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip())
    except: return 8.0
def clipfile(bid):
    f=S["beats"].get(bid,{}).get("job",{}).get("file")
    return f if f and os.path.exists(f) else None

DRIFT_ABS=argf("--driftabs",0.40)   # a frame this low is "clearly not Candice"
MINLOW=argf("--minlow",3)           # need this many low frames to call sustained drift (avoids transient profiles)
# pass 1: gather per-clip frame sims
data=[]
for b in M["beats"]:
    cf=clipfile(b["id"])
    if not cf: continue
    d=dur(cf); sims=[]
    for k in range(NFR):
        t=d*(k+0.5)/NFR
        jpg=f"/tmp/_fs_{os.getpid()}.jpg"
        subprocess.run([FF,"-y","-ss",f"{t:.2f}","-i",cf,"-frames:v","1","-vf","scale=640:-1",jpg],capture_output=True)
        if not os.path.exists(jpg): continue
        img=cv2.imread(jpg); os.remove(jpg)
        r=emb_of(img)
        if not r or r[0] is None: continue
        e,ds=r
        if ds<0.55: continue
        sims.append((cos(e),cosi(e)))               # (sim_candice, sim_imposter)
    data.append((b["id"],b["type"],sims))
# 2-class verdict: a frame "leans imposter" when sim_imposter > sim_candice (delta<0).
NEG=argf("--neg",-0.02)        # delta below this = clearly imposter-leaning frame
IMPN=int(argf("--impn",4))     # this many imposter-leaning frames => the clip is the imposter
rows=[]; flagged=[]; review=[]
for bid,typ,sims in data:
    if not sims:
        rows.append((bid,typ,None,None,0,0,"PASS-noface")); continue
    bestc=max(s[0] for s in sims)
    deltas=[s[0]-s[1] for s in sims]
    nimp=sum(1 for dl in deltas if dl<NEG)
    md=round(sum(deltas)/len(deltas),3)
    verdict="PASS"
    if typ=="character":
        if nimp>=IMPN: verdict="FLAG-imposter"        # majority of frames are the imposter face
        elif nimp>=2: verdict="REVIEW"                # ambiguous -> eyeball at full res
    else:
        if nimp>=3: verdict="FLAG-brollface"
    if verdict=="FLAG-imposter" or verdict=="FLAG-brollface": flagged.append(bid)
    if verdict=="REVIEW": review.append(bid)
    rows.append((bid,typ,round(bestc,3),md,nimp,len(sims),verdict))
print(f"\n{'id':12} {'type':10} {'bestC':>6} {'mΔ':>6} {'nimp':>4} {'nf':>3}  verdict")
for r in sorted(rows,key=lambda x:(x[4] if x[4] is not None else -1),reverse=True):
    print(f"{r[0]:12} {r[1]:10} {str(r[2]):>6} {str(r[3]):>6} {r[4]:>4} {r[5]:>3}  {r[6]}")
print(f"\nFLAGGED ({len(flagged)}): {','.join(flagged)}")
print(f"REVIEW ({len(review)}): {','.join(review)}")
if JOUT: json.dump({"flagged":flagged,"review":review,
    "rows":[{"id":r[0],"type":r[1],"bestC":r[2],"meanDelta":r[3],"nimp":r[4],"verdict":r[6]} for r in rows]},open(JOUT,"w"))
