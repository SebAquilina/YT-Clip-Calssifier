#!/usr/bin/env python3
"""
trim_and_place.py — turn the per-beat 8 s clips into one body_<n>.mp4 timed to the
segment narration.

Each Veo clip is ~8 s; each beat is 6-9 s. For every beat in order: trim (or, if
the beat is longer than the clip, hold by chaining a second clip — handled at
generation, not here) the clip to its beat duration, drop its Veo audio, then
concat all beat clips and lay the segment narration MP3 over the result.

  python3 trim_and_place.py --beats beats_1.json --clips-dir "Source clips/broll" \
      --narration body_1.mp3 --out body_1.mp4

Rules enforced:
  - trim from the MIDDLE-out, dropping the inhale-y last 0.3 s of each clip
  - never freeze-hold a frame to fill time (a held frame is an instant AI tell);
    a beat longer than its clip must have been split upstream
  - no identical clip back-to-back (warns if two adjacent beats share a file)
"""
import argparse, json, os, subprocess, sys, tempfile

TAIL_TRIM = 0.30   # drop the inhale-y tail

def probe_dur(path):
    out = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=nw=1:nk=1", path], capture_output=True, text=True).stdout.strip()
    return float(out) if out else 0.0

def trim_clip(src, dur, dst):
    """Take a centered `dur` seconds of src (minus the tail), strip audio, 16:9."""
    src_dur = probe_dur(src)
    usable = max(0.1, src_dur - TAIL_TRIM)
    take = min(dur, usable)
    start = max(0.0, (usable - take) / 2.0)     # middle-out
    subprocess.run(["ffmpeg","-y","-ss",f"{start:.2f}","-i",src,"-t",f"{take:.2f}",
        "-an","-vf","scale=1280:720:force_original_aspect_ratio=increase,"
        "crop=1280:720,fps=24","-c:v","libx264","-pix_fmt","yuv420p",
        "-r","24", dst], check=True, capture_output=True)
    return take

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--beats", required=True)
    ap.add_argument("--clips-dir", required=True)
    ap.add_argument("--narration", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data = json.load(open(args.beats))
    beats = data["beats"] if "beats" in data else data
    tmp = tempfile.mkdtemp(prefix="place_")
    parts, prev_file = [], None
    for b in beats:
        clip = b.get("file") or os.path.join(args.clips_dir, f"{b['id']}.mp4")
        if not os.path.exists(clip):
            print(f"[error] missing clip for {b['id']}: {clip}", file=sys.stderr)
            sys.exit(2)
        if clip == prev_file:
            print(f"[warn] {b['id']} reuses the previous clip back-to-back")
        dst = os.path.join(tmp, f"{b['id']}.mp4")
        got = trim_clip(clip, b["dur"], dst)
        if got < b["dur"] - 0.5:
            print(f"[warn] {b['id']} beat {b['dur']:.1f}s but clip only {got:.1f}s "
                  f"(split this beat upstream or chain a 2nd clip — NOT freeze-held)")
        parts.append(dst); prev_file = clip

    # concat video parts
    listf = os.path.join(tmp, "list.txt")
    open(listf,"w").write("".join(f"file '{p}'\n" for p in parts))
    silent = os.path.join(tmp, "video_only.mp4")
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",listf,
        "-c","copy", silent], check=True, capture_output=True)

    # lay narration over it; match to the shorter of the two
    subprocess.run(["ffmpeg","-y","-i",silent,"-i",args.narration,
        "-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-shortest",
        args.out], check=True, capture_output=True)

    vd, ad = probe_dur(silent), probe_dur(args.narration)
    print(f"[ok] {args.out}  video {vd:.1f}s / narration {ad:.1f}s  ({len(parts)} beats)")
    if abs(vd-ad) > 1.5:
        print(f"[warn] video/narration drift {vd-ad:+.1f}s — add/trim a beat to align")

if __name__ == "__main__":
    main()
