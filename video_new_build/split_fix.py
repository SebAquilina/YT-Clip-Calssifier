"""split_fix.py <proj> <comma-separated cut beat ids>
Splits each over-long TH beat into two beats (<id> + <id>s) that each fit in 8s,
preserving all content. Manifest surgery only — existing beat IDs unchanged (no cascade).
Prints the beat IDs to (re)generate."""
import json,sys,re
proj=sys.argv[1]; ids=[x for x in sys.argv[2].split(",") if x]
PF=f"{proj}/Project files"; M=json.load(open(f"{PF}/manifest.json"))
beats=M["beats"]; chains=M.get("chains",[])
def split_sentence(s):
    words=s.split(); n=len(words)
    mid=n//2
    # candidate split points = comma positions; pick nearest to mid
    commas=[i+1 for i,w in enumerate(words) if w.endswith(",")]
    pts=commas if commas else [mid]
    sp=min(pts,key=lambda p:abs(p-mid))
    if sp<4 or sp>n-3: sp=mid
    s1=" ".join(words[:sp]).rstrip(",")+"."
    s2=" ".join(words[sp:])
    s2=s2[0].upper()+s2[1:]
    return s1,s2
def beat_index(bid):
    for i,b in enumerate(beats):
        if b["id"]==bid: return i
    return -1
regen=[]
for bid in ids:
    i=beat_index(bid)
    if i<0: print(f"  !! {bid} not found",file=sys.stderr); continue
    b=beats[i]; S=b["sentence"]; s1,s2=split_sentence(S)
    newid=bid.replace("_th","s_th")
    if any(b2["id"]==newid for b2 in beats):
        print(f"  {bid} already split -> {newid}",file=sys.stderr); regen+=[bid,newid]; continue
    # part 1 keeps bid
    b["prompt"]=b["prompt"].replace(S,s1); b["sentence"]=s1
    # part 2 = new beat, same scene context, S2
    nb={"id":newid,"type":"character","sentence":s2,"dur":b.get("dur",8.0),
        "prompt":b["prompt"].replace(s1,s2)}
    beats.insert(i+1,nb)
    # add to the chain containing bid
    for c in chains:
        if bid in c["beat_ids"]:
            ci=c["beat_ids"].index(bid); c["beat_ids"].insert(ci+1,newid); break
    regen+= [bid,newid]
    print(f"  split {bid}: '{s1}' || '{s2}'  -> new {newid}",file=sys.stderr)
json.dump(M,open(f"{PF}/manifest.json","w"),indent=2)
print(",".join(regen))
