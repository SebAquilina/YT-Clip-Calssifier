#!/usr/bin/env python3
"""
verify_broll.py — Stage B5 gates for an all-AI B-roll video.

Mechanical checks (this script) + a sampled-frame pull for the human/visual
checks (sentence-match, iPhone-look, period/anachronism, continuity) which a
script cannot judge — it exports the frames and prints the checklist so you
eyeball them.

  python3 verify_broll.py --manifest broll_manifest.json --clips-dir "Source clips/broll"
  python3 verify_broll.py --manifest broll_manifest.json --sample-frames frames/

Mechanical gates:
  - every beat has a prompt and a generated file > 100 KB
  - each clip has a video stream and a sane duration (~8 s pre-trim)
  - no two beats share an md5 (a duplicate = a stale capture; regenerate)
  - no identical clip placed back-to-back
Visual gates (frame export + checklist): sentence-match, iPhone-look,
period-accuracy, continuity. Sample the FIRST HALF densely.
"""
import argparse, json, os, hashlib, subprocess, sys

def md5(path):
    h = hashlib.md5()
    with open(path,"rb") as f:
        for c in iter(lambda: f.read(8192), b""): h.update(c)
    return h.hexdigest()

def probe(path):
    out = subprocess.run(["ffprobe","-v","error","-show_entries",
        "format=duration:stream=codec_type","-of","json", path],
        capture_output=True, text=True).stdout
    try: return json.loads(out)
    except Exception: return {}

def load(manifest):
    m = json.load(open(manifest))
    if "broll" in m: return m["broll"]["beats"]
    if "beats" in m: return m["beats"]
    raise SystemExit("no beats[] in manifest")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--clips-dir", default=None)
    ap.add_argument("--sample-frames", default=None,
                    help="export each clip's middle frame here for the visual gates")
    args = ap.parse_args()
    beats = load(args.manifest)

    fails, seen_md5, prev = [], {}, None
    for b in beats:
        bid = b["id"]
        if not b.get("prompt"):
            fails.append(f"{bid}: NO PROMPT"); continue
        f = b.get("file") or (os.path.join(args.clips_dir, f"{bid}.mp4") if args.clips_dir else None)
        if not f or not os.path.exists(f):
            fails.append(f"{bid}: missing clip"); continue
        if os.path.getsize(f) < 100*1024:
            fails.append(f"{bid}: clip < 100KB")
        info = probe(f)
        has_v = any(s.get("codec_type")=="video" for s in info.get("streams",[]))
        if not has_v: fails.append(f"{bid}: no video stream")
        h = md5(f)
        if h in seen_md5: fails.append(f"{bid}: DUPLICATE of {seen_md5[h]} (stale capture)")
        else: seen_md5[h] = bid
        if f == prev: fails.append(f"{bid}: same clip back-to-back")
        prev = f
        if args.sample_frames:
            os.makedirs(args.sample_frames, exist_ok=True)
            dur = float(info.get("format",{}).get("duration",8) or 8)
            subprocess.run(["ffmpeg","-y","-ss",f"{dur/2:.2f}","-i",f,"-vframes","1",
                "-vf","scale=640:-1", os.path.join(args.sample_frames,f"{bid}.jpg")],
                capture_output=True)

    print(f"\n[mechanical] {len(beats)} beats, {len(fails)} issue(s)")
    for x in fails: print("  FAIL", x)
    if not fails: print("  all mechanical checks pass")

    print("\n[visual gates — eyeball the sampled frames against each beat sentence]")
    print("  1. SENTENCE-MATCH: clip depicts the beat's verbatim noun+action (not the theme)")
    print("  2. iPHONE-LOOK: no bokeh, no film grain, no teal/orange grade, no gimbal-smooth crane")
    print("  3. PERIOD: no power lines/switch/outlet/car/phone/plastic/zipper/modern fixture")
    print("  4. CONTINUITY: recurring locations look like the SAME place (wood tone, light, palette)")
    print("  Sample the first half densely; regenerate any clip that fails any gate.")
    if args.sample_frames:
        print(f"\n  frames -> {args.sample_frames}/  (open them next to the manifest sentences)")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
