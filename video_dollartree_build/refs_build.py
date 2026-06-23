#!/usr/bin/env python3
"""refs_build.py [stage] — build high-quality, consistent reference images for the pipeline.

stage 1 (default): generate CANDIDATES for the canonical workbench + each TH scene
  (Candice at bench/kitchen/shelf/packing/window), several per slot, into reference_build/.
  A human/vision pass then picks the best of each. Uses Candice's face ref (+ the chosen bench)
  as img2img references so identity & the wooden bench stay consistent. iPhone-real, sharp.
stage select: given chosen filenames (reference_build/SELECTED.json), host them on litterbox and
  write /tmp/bench_ref.txt + /tmp/scene_refs.json so imgkit picks up the new keyframes.

Why: Veo uses the keyframe as the clip's first frame; a soft ~768p anchor => soft talking head.
A sharp, iPhone-real, identity-locked scene keyframe is the single biggest TH-quality lever.
"""
import os, sys, json, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import imgkit as K
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","reference_build"); os.makedirs(OUT,exist_ok=True)
NCAND=int(os.environ.get("NCAND","3"))

def host(path):
    for _ in range(6):
        r=subprocess.run(["curl","-s","-m","120","-F","reqtype=fileupload","-F","time=72h","-F",
            f"fileToUpload=@{path}","https://litterbox.catbox.moe/resources/internals/api.php"],capture_output=True,text=True)
        if r.stdout.strip().startswith("http"): return r.stdout.strip()
        time.sleep(4)
    return None

# Candice identity reference (already in repo as a clean 16:9 face/scene)
CANDICE_LOCAL="/tmp/_ref_full.jpg" if os.path.exists("/tmp/_ref_full.jpg") else None

BENCH_PROMPT=(
 "A casual iPhone photo of an empty rustic wooden candle-making workbench in a lived-in home workshop: "
 "a worn warm-toned wooden tabletop with a few finished glass jar candles, a soy-wax pitcher, small amber "
 "fragrance bottles and a kitchen thermometer pushed to one side, a curing shelf of candles softly out of "
 f"focus behind, soft natural window light from the left. {K.IPHONE} {K.NOTEXT}")

SCENE_PROMPTS={
 "bench":"seated at her rustic wooden candle-workshop workbench, hands resting near a few finished jar candles, looking straight at the camera with a warm relaxed closed-mouth expression",
 "kitchen":"standing at her kitchen stove station with a wax-melting pot, looking straight at the camera, warm relaxed closed-mouth expression",
 "shelf":"standing beside her curing shelf full of finished jar candles, looking straight at the camera, warm relaxed closed-mouth expression",
 "packing":"standing at her packing table with kraft boxes and finished candles, looking straight at the camera, warm relaxed closed-mouth expression",
 "window":"seated by a bright window at a small side table with a couple of candles, looking straight at the camera, warm relaxed closed-mouth expression",
}
def scene_prompt(desc):
    return (f"A casual iPhone vlog photo. {K.IDENTITY}She is {desc}. Medium shot, she fills the centre of a 16:9 frame "
    f"with room around her, framed like a YouTube talking-head first frame. {K.IPHONE} {K.NOTEXT} Setting: {K.WS}")

def gen_stage1():
    # 1) bench candidates (no people)
    for i in range(NCAND):
        d=os.path.join(OUT,f"bench_cand{i}.png")
        if not os.path.exists(d):
            print(f"[bench] candidate {i}",flush=True)
            K.gen_image(BENCH_PROMPT, d, aspect="16:9")
    # 2) scene candidates (identity-locked via Candice ref)
    cref=[K.CANDICE_REF] if K.CANDICE_REF else None
    for scene,desc in SCENE_PROMPTS.items():
        for i in range(NCAND):
            d=os.path.join(OUT,f"{scene}_cand{i}.png")
            if not os.path.exists(d):
                print(f"[{scene}] candidate {i}",flush=True)
                K.gen_image(scene_prompt(desc), d, image_urls=cref, aspect="16:9")
    print("STAGE1 DONE — candidates in reference_build/. Pick best into SELECTED.json then run: refs_build.py select")

def do_select():
    sel=json.load(open(os.path.join(OUT,"SELECTED.json")))   # {"bench":"bench_cand1.png","scenes":{"bench":"bench_cand0.png",...}}
    out={"scenes":{}}
    bench_path=os.path.join(OUT,sel["bench"]); burl=host(bench_path)
    out["bench"]=burl; open("/tmp/bench_ref.txt","w").write(burl)
    for scene,fn in sel["scenes"].items():
        u=host(os.path.join(OUT,fn)); out["scenes"][scene]=u; print(scene,"->",u)
    json.dump(out,open("/tmp/scene_refs.json","w"),indent=2)
    print("SELECT DONE — /tmp/scene_refs.json + /tmp/bench_ref.txt written")

if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=="select": do_select()
    else: gen_stage1()
