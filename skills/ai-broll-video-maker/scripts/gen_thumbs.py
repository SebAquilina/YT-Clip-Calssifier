#!/usr/bin/env python3
"""gen_thumbs.py <project_dir> <prompts.json>   (v6.3)
Generate YouTube thumbnails from the sheet's NANO PROMPTs — exactly as given (they render their own
title text). For EACH prompt we generate TWO variants at 2K on nano-banana-PRO, with Candice's face
reference fed in so her likeness matches. Saved with a consistent naming convention into
<project>/thumbnails/  as  thumb_<label>_v1.png / thumb_<label>_v2.png .

prompts.json = [{"label":"A_biggest_mistakes","prompt":"<full NANO PROMPT...>"}, ...]
"""
import os, sys, json, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import imgkit as K
PROJ=sys.argv[1]; PROMPTS=json.load(open(sys.argv[2]))
OUT=os.path.join(PROJ,"thumbnails"); os.makedirs(OUT,exist_ok=True)
REF=[K.CANDICE_REF] if K.CANDICE_REF else None
def one(label, prompt, v):
    dest=os.path.join(OUT,f"thumb_{label}_v{v}.png")
    if os.path.exists(dest) and os.path.getsize(dest)>20000: print("have",dest,flush=True); return dest
    ok=K.gen_image(prompt, dest, image_urls=REF, aspect="16:9", model=K.THUMB_MODEL, resolution=K.THUMB_RES, tries=6)
    print(("OK  " if ok else "FAIL")+f" thumb_{label}_v{v}",flush=True)
    return dest if ok else None
jobs=[(p["label"],p["prompt"],v) for p in PROMPTS for v in (1,2)]
with cf.ThreadPoolExecutor(max_workers=4) as ex:
    list(ex.map(lambda a: one(*a), jobs))
print("THUMBS DONE ->",OUT, sorted(os.listdir(OUT)),flush=True)
