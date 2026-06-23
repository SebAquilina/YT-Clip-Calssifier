#!/usr/bin/env python3
"""bootstrap_local.py — make the pipeline run on a laptop with NO GitHub dependency.

The only GitHub touch in the code is the DEFAULT public URL for the reference keyframe images
(Candice + the 5 scene anchors + hands). Those image FILES are committed in this repo, so this script
uploads them from disk to a public host (litterbox) ONCE and writes the override files that imgkit.py
already prefers (/tmp/scene_refs.json, /tmp/raw_ref.txt, /tmp/bench_ref.txt). After running this, the
pipeline never calls github.

Also writes /tmp/apikey.txt from $LABS69_API_KEY.

What still needs the internet (inherent to cloud AI generation — cannot be offline):
  - 69labs.vip  (image/video/TTS generation)
  - a public image host (litterbox) so 69labs can fetch your reference/keyframe images server-side
Run once per machine/session:  LABS69_API_KEY=vk_... python3 bootstrap_local.py
"""
import os, sys, json, subprocess
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))   # repo root from video_dollartree_build/
PS=os.path.join(ROOT,"video_ps_veo","assets"); VB=os.path.join(ROOT,"video_build","assets")
ASSETS={
 "candice": os.path.join(VB,"candice_ref_16x9.jpg"),
 "bench":   os.path.join(PS,"bench_anchor.png"),
 "kitchen": os.path.join(PS,"kitchen_anchor.png"),
 "shelf":   os.path.join(PS,"shelf_anchor.png"),
 "packing": os.path.join(PS,"packing_anchor.png"),
 "window":  os.path.join(PS,"window_anchor.png"),
}
def upload(path):
    if not os.path.exists(path): print("  MISSING",path); return None
    for _ in range(5):
        r=subprocess.run(["curl","-s","-m","120","-F","reqtype=fileupload","-F","time=72h",
            "-F",f"fileToUpload=@{path}","https://litterbox.catbox.moe/resources/internals/api.php"],
            capture_output=True,text=True)
        if r.stdout.strip().startswith("http"): return r.stdout.strip()
    return None

def main():
    key=os.environ.get("LABS69_API_KEY")
    if key: open("/tmp/apikey.txt","w").write(key.strip()); print("wrote /tmp/apikey.txt")
    elif os.path.exists("/tmp/apikey.txt"): print("/tmp/apikey.txt already present")
    else: print("WARNING: set LABS69_API_KEY (or create /tmp/apikey.txt) — generation needs it")
    urls={}
    print("uploading reference images to a public host (so 69labs can fetch them)…")
    for name,p in ASSETS.items():
        u=upload(p); urls[name]=u; print(f"  {name}: {u}")
    if not urls.get("candice") or not urls.get("bench"):
        print("FAILED to host the essential refs (need internet to litterbox)"); sys.exit(1)
    scenes={k:urls[k] for k in ("bench","kitchen","shelf","packing","window") if urls.get(k)}
    json.dump({"scenes":scenes,"candice":urls["candice"],"bench":urls["bench"]}, open("/tmp/scene_refs.json","w"), indent=2)
    open("/tmp/raw_ref.txt","w").write(urls["candice"])
    open("/tmp/bench_ref.txt","w").write(urls["bench"])
    print("wrote /tmp/scene_refs.json, /tmp/raw_ref.txt, /tmp/bench_ref.txt — pipeline is now github-free.")
    print("NOTE: litterbox links last 72h; re-run this to refresh, or host the 6 images permanently and "
          "paste the URLs into /tmp/scene_refs.json (+ raw_ref.txt/bench_ref.txt).")

if __name__=="__main__": main()
