#!/usr/bin/env python3
"""gen_dt.py <project_dir> — generate every beat's asset by visual_mode.
  talking_head / image_split TH-pane : veo TH clip (veo voice)
  image_full / image_live narration  : cloned-voice TTS
  image_full / image_split still      : nano-banana image
  image_live                          : nano-banana still -> veo come-to-life (keyframes)
  broll                               : veo hands (muted) + cloned TTS
Sequential (no state race), resumable, robust. State in Project files/state.json."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imgkit as K
PROJ=sys.argv[1]; PF=os.path.join(PROJ,"Project files")
SRC=os.path.join(PROJ,"Source clips"); IMG=os.path.join(PROJ,"images"); AUD=os.path.join(PF,"audio")
for d in (SRC,IMG,AUD): os.makedirs(d,exist_ok=True)
M=json.load(open(os.path.join(PF,"manifest.json")))
# optional sharding: --shard I/N -> this worker handles only beats where index%N==I, with its OWN
# state file (state_sI.json). Disjoint shards never write the same file => no state race. Run up to
# ~5 shards in parallel (matches veo's 5-concurrent limit), then merge_state.py combines them.
SHARD=None; NSH=1
if "--shard" in sys.argv:
    SHARD,NSH=map(int,sys.argv[sys.argv.index("--shard")+1].split("/"))
SP=os.path.join(PF,f"state_s{SHARD}.json") if SHARD is not None else os.path.join(PF,"state.json")
S=json.load(open(SP)) if os.path.exists(SP) else {"beats":{}}
def save(): json.dump(S,open(SP,"w"),indent=2)
def st(bid): return S["beats"].setdefault(bid,{})
def have(p): return p and os.path.exists(p) and os.path.getsize(p)>2000
def vid_ok(p):
    return have(p) and K.dur(p)>0.4

for idx,b in enumerate(M["beats"]):
    if SHARD is not None and idx%NSH!=SHARD: continue
    bid=b["id"]; vm=b.get("visual_mode",b.get("type")); e=st(bid)
    # --- TH clip (talking_head + image_split need a veo TH clip) ---
    if vm in ("talking_head","image_split"):
        clip=os.path.join(SRC,f"{bid}.mp4")
        if not vid_ok(e.get("clip")):
            print(f"[{bid}] veo TH ({vm})",flush=True)
            ok=K.gen_video(b["prompt"], clip, image_urls=[b["seed"]], mode="keyframes", muted=False)
            if ok: e["clip"]=os.path.abspath(clip); save()
    # --- still image (image_full + image_split + image_live first frame) ---
    if vm in ("image_full","image_split","image_live"):
        img=os.path.join(IMG,f"{bid}.png")
        if not have(e.get("image")):
            print(f"[{bid}] image still",flush=True)
            # reference = explicit per-beat ref, else the canonical bench (keeps wood+light consistent)
            refs=[b["image_ref_url"]] if b.get("image_ref_url") else ([K.BENCH_REF] if K.BENCH_REF else None)
            ar=b.get("ar","16:9")   # split panes are near-square -> 1:1 so they are not squeezed
            if K.gen_image(b["image_prompt"], img, image_urls=refs, aspect=ar): e["image"]=os.path.abspath(img); save()
    # --- come-to-life: animate the still ---
    if vm=="image_live":
        clip=os.path.join(SRC,f"{bid}.mp4")
        if not vid_ok(e.get("clip")) and have(e.get("image")):
            print(f"[{bid}] come-to-life (img2video)",flush=True)
            # host the still on a stable temp url for ingredients/keyframes
            up=K.req  # reuse litterbox host for the keyframe
            import subprocess
            url=None
            for _ in range(5):
                r=subprocess.run(["curl","-s","-m","90","-F","reqtype=fileupload","-F","time=72h","-F",
                    f"fileToUpload=@{e['image']}","https://litterbox.catbox.moe/resources/internals/api.php"],capture_output=True,text=True)
                if r.stdout.strip().startswith("http"): url=r.stdout.strip(); break
            if url and K.gen_video(K.live_motion(b["motion"]), clip, image_urls=[url], mode="keyframes", muted=True):
                e["clip"]=os.path.abspath(clip); save()
    # --- B-roll hands (muted) ---
    if vm=="broll":
        clip=os.path.join(SRC,f"{bid}.mp4")
        if not vid_ok(e.get("clip")):
            print(f"[{bid}] veo B-roll hands",flush=True)
            if K.gen_video(b["prompt"], clip, image_urls=[b.get("broll_ref",K.HANDS)], mode="keyframes", muted=True):
                e["clip"]=os.path.abspath(clip); save()
    # --- TTS narration (image_full, image_live, broll) ---
    if vm in ("image_full","image_live","broll") and b.get("narration"):
        mp3=os.path.join(AUD,f"{bid}.mp3")
        if not have(e.get("audio")):
            print(f"[{bid}] TTS narration",flush=True)
            for _ in range(3):
                if K.tts(b["narration"], mp3): e["audio"]=os.path.abspath(mp3); e["adur"]=K.dur(mp3); save(); break
    save()
# report (this shard's beats only)
mine=[b for i,b in enumerate(M["beats"]) if SHARD is None or i%NSH==SHARD]
done=sum(1 for b in mine if (lambda vm,e: (
    (vm in("talking_head","image_split") and vid_ok(e.get("clip"))) or
    (vm=="image_full" and have(e.get("image")) and have(e.get("audio"))) or
    (vm=="image_live" and vid_ok(e.get("clip")) and have(e.get("audio"))) or
    (vm=="broll" and vid_ok(e.get("clip")) and have(e.get("audio")))
))(b.get("visual_mode",b.get("type")), st(b["id"])))
print(f"GEN DONE{'' if SHARD is None else ' shard '+str(SHARD)}: {done}/{len(mine)} beats complete",flush=True)
