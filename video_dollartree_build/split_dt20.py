#!/usr/bin/env python3
"""split_dt20.py — split over-long veo-spoken beats (TH + split) into <=~17-word halves so veo's
8s cap never truncates them. Operates on the existing manifest+state WITHOUT renumbering (derives
new IDs bNNb_*), reuses each beat's existing prompt (swaps the quoted sentence), adds a hard-stop
to part 1, copies the split image for part 2, and pops part-1 clips so they regenerate.
Reads the truncated-id list from /tmp/dt_trunc.json (or arg list)."""
import json, os, re, sys, shutil
PF="video_dt20_veo/Project files"
M=json.load(open(PF+"/manifest.json")); S=json.load(open(PF+"/state.json"))
flagged=set(json.load(open("/tmp/dt_trunc.json"))["truncated"]) if os.path.exists("/tmp/dt_trunc.json") else set()
if len(sys.argv)>1: flagged=set(sys.argv[1].split(","))
HARDSTOP=" Speak only this one sentence, then stop talking and hold still in silence — do not start the next thought."
def split_sentence(s):
    words=s.split()
    if len(words)<=18: return [s]
    # try to split at a sentence/clause boundary nearest the middle
    mid=len(words)/2; best=None; bestd=1e9
    toks=s.replace("—","— ").split()
    # find boundary indices (word ends with . ! ? , ; : or em dash)
    acc=[]; idx=0; bounds=[]
    for i,w in enumerate(words):
        if re.search(r"[.!?,;:]$", w) or w=="—": bounds.append(i+1)
    for bi in bounds:
        if bi<3 or bi>len(words)-3: continue
        d=abs(bi-mid)
        if d<bestd and max(bi,len(words)-bi)<=18: bestd=d; best=bi
    if best is None:
        best=int(round(mid))  # hard split at midpoint
    p1=" ".join(words[:best]).strip(); p2=" ".join(words[best:]).strip()
    return [p1,p2]
def swap_quote(prompt,new):
    return re.sub(r'saying exactly: ".*?"', f'saying exactly: "{new}"', prompt, count=1)

beats=M["beats"]; out=[]; nsplit=0; popped=[]
for b in beats:
    if b["id"] in flagged and b["visual_mode"] in ("talking_head","image_split"):
        parts=split_sentence(b["sentence"])
        if len(parts)==1: out.append(b); continue
        p1,p2=parts[0],parts[1]
        # part 1 keeps the id; new prompt + hard stop; pop its clip to regen
        b1=dict(b); b1["sentence"]=p1; b1["prompt"]=swap_quote(b["prompt"],p1)+HARDSTOP
        S["beats"].get(b["id"],{}).pop("clip",None); popped.append(b["id"])
        # part 2 = new beat
        nb=dict(b); nb["id"]=b["id"].replace("_","b_",1) if False else re.sub(r"_(\w+)$", r"b_\1", b["id"])
        nb["sentence"]=p2; nb["prompt"]=swap_quote(b["prompt"],p2)
        # ensure fresh state for part2
        S["beats"][nb["id"]]=S["beats"].get(nb["id"],{})
        S["beats"][nb["id"]].pop("clip",None)
        if b["visual_mode"]=="image_split":
            # copy the image so part 2 also shows it
            src=S["beats"].get(b["id"],{}).get("image")
            if src and os.path.exists(src):
                dst=os.path.join("video_dt20_veo","images",f"{nb['id']}.png"); shutil.copy(src,dst)
                S["beats"][nb["id"]]["image"]=os.path.abspath(dst)
        out.append(b1); out.append(nb); nsplit+=1
    else:
        out.append(b)
M["beats"]=out
json.dump(M,open(PF+"/manifest.json","w"),indent=2)
json.dump(S,open(PF+"/state.json","w"),indent=2)
print(f"split {nsplit} beats -> manifest now {len(out)} beats; popped {len(popped)} part-1 clips for regen")
