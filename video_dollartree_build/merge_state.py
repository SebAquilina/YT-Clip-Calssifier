#!/usr/bin/env python3
"""merge_state.py <project_dir> — merge all Project files/state_s*.json shard states into the
canonical state.json the assembler reads. Later/non-empty entries win per beat. Idempotent."""
import sys, os, json, glob
PROJ=sys.argv[1]; PF=os.path.join(PROJ,"Project files")
merged={"beats":{}}
base=os.path.join(PF,"state.json")
if os.path.exists(base): merged=json.load(open(base))
for sf in sorted(glob.glob(os.path.join(PF,"state_s*.json"))):
    s=json.load(open(sf))
    for bid,e in s.get("beats",{}).items():
        if not e: continue
        cur=merged["beats"].setdefault(bid,{})
        cur.update({k:v for k,v in e.items() if v})
json.dump(merged,open(base,"w"),indent=2)
print(f"merged {len(merged['beats'])} beats from {len(glob.glob(os.path.join(PF,'state_s*.json')))} shards -> state.json")
