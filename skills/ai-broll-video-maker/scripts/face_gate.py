#!/usr/bin/env python3
"""face_gate.py <project_dir> [--list | --regen b12_th,b34_g3]
STRICT per-section face gate (vision-agent panel workflow).

A wrong face must NEVER reach the final cut, so every talking-head AND B-roll
section is verified to be the channel character (Candice) before assembly.

Because no face-recognition lib is installed, the verdict is rendered by a panel
of vision sub-agents (orchestrated by the parent): this script only does the
deterministic parts —
  --list : extract 2 frames per section (mid + late) to /tmp/facegate/<bid>_{a,b}.jpg
           and print a JSON array [{id,type,scene,frames:[...]}]. The parent hands
           each batch + the reference photo to a vision agent that returns MATCH or
           MISMATCH per id (MATCH = clearly the same woman; B-roll hands-only clips
           with no face also pass as long as no WRONG person appears).
  --regen : regenerate the listed mismatch sections (via regen_clip.py, which seeds
           TH from the section's clean scene anchor and B-roll from its hands ref),
           so they can be re-checked. Loop list->judge->regen until all MATCH.
The reference photo is manifest['reference_photo_url'] (download once for the agents)."""
import sys, os, json, subprocess, glob
FF="/usr/local/bin/ffmpeg"
PROJ=sys.argv[1]; PF=os.path.join(PROJ,"Project files")
M=json.load(open(os.path.join(PF,"manifest.json"))); S=json.load(open(os.path.join(PF,"state.json")))
OUT="/tmp/facegate"; os.makedirs(OUT,exist_ok=True)
def clipfile(bid):
    f=S["beats"].get(bid,{}).get("job",{}).get("file")
    return f if f and os.path.exists(f) else None
def scene_of(bid):
    for c in M.get("chains",[]):
        if bid in c.get("beat_ids",[]): return c["scene"]
    return "broll" if any(b["id"]==bid and b["type"]=="broll" for b in M["beats"]) else "?"

if "--regen" in sys.argv:
    ids=sys.argv[sys.argv.index("--regen")+1].split(",")
    rg=os.path.join(os.path.dirname(os.path.abspath(__file__)),"regen_clip.py")
    for bid in ids:
        bid=bid.strip()
        if not bid: continue
        print("REGEN",bid,flush=True)
        subprocess.run(["python3",rg,PROJ,bid],env={**os.environ})
    sys.exit(0)

# default / --list : extract frames + print manifest
out=[]
for b in M["beats"]:
    cf=clipfile(b["id"])
    if not cf: continue
    frames=[]
    d=subprocess.run([FF.replace("ffmpeg","ffprobe"),"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",cf],capture_output=True,text=True).stdout.strip()
    try: dur=float(d)
    except: dur=8.0
    for tag,t in (("a",dur*0.4),("b",dur*0.8)):
        fp=os.path.join(OUT,f"{b['id']}_{tag}.jpg")
        subprocess.run([FF,"-y","-ss",f"{t:.2f}","-i",cf,"-frames:v","1","-vf","scale=480:270",fp],capture_output=True)
        if os.path.exists(fp): frames.append(fp)
    out.append({"id":b["id"],"type":b["type"],"scene":scene_of(b["id"]),"frames":frames})
print(json.dumps(out))
