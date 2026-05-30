"""Command-line interface.

  ytclip search "candle making diy" -n 10
  ytclip prepare <video_id> [--no-stream]      # download/storyboard -> windows -> sheets -> labels stub
  ytclip finalize <video_id>                   # labels.json -> rules engine -> timeline + md
  ytclip learn                                 # aggregate all timelines -> learned_rules.yaml + SUMMARY.md
  ytclip prompt                                # print the classification prompt + label reference
"""
from __future__ import annotations

import argparse
import json
import sys

from . import download, pipeline
from .learn import learn as run_learn
from .taxonomy import load_taxonomy, prompt_label_reference

CLASSIFY_PROMPT = """\
You are classifying a candle-making (DIY) tutorial video. You are shown a contact
sheet: each tile is one 5-10s WINDOW, captioned `W{index}  {start}-{end}s`, and
shows that window's representative frame(s) left-to-right in time.

For EACH window tile output:
  {"window": <int>, "label": "<id>", "confidence": 0.0-1.0, "description": "<detailed grounded text>"}

DESCRIPTION PROTOCOL (detailed + anti-hallucination):
  1. Describe only what is VISIBLE: the vessel/material, the tool, what the hands
     are doing, colours. Be specific ("a metal pitcher of cream wax is stirred
     with a wooden stick over a double boiler"), not vague ("making a candle").
  2. Do NOT invent details you cannot see. If a tile is blurry/ambiguous, say so,
     use `other_unclear`, and lower confidence. Prefer "appears to" for guesses.
  3. Quote on-screen text ONLY if you can actually read it; it will be checked
     against OCR (config/filter.yaml) and contradictions are flagged.
  4. Separate observation (what is shown) from inference (the chosen label).
  5. Confidence reflects grounding: thin evidence -> <=0.5.

Windows that are a presenter talking to camera, or a pure title/end/text card,
are auto-detected and labelled by objective detectors (face + OCR) - you only
need to describe the hands-on action windows. Labels:
"""


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(prog="ytclip")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("-n", type=int, default=10)
    p = sub.add_parser("prepare"); p.add_argument("video_id")
    p.add_argument("--no-stream", action="store_true", help="skip stream download, use storyboards")
    p.add_argument("--max-height", type=int, default=480)
    f = sub.add_parser("finalize"); f.add_argument("video_id")
    sub.add_parser("learn")
    an = sub.add_parser("analyze", help="compute objective features (face/text/OCR/motion) per window")
    an.add_argument("video_id", nargs="?", help="one video, or omit for all finalized videos")
    an.add_argument("--no-ocr", action="store_true")
    sub.add_parser("build-db")
    sub.add_parser("prompt")

    a = ap.parse_args(argv)

    if a.cmd == "search":
        for v in download.search(a.query, n=a.n):
            print(f"{v.id}\t{int(v.duration)//60}m{int(v.duration)%60:02d}\t{v.title}")
    elif a.cmd == "prepare":
        m = pipeline.prepare(a.video_id, prefer_stream=not a.no_stream, max_height=a.max_height)
        stub = pipeline.make_label_stub(a.video_id)
        print(f"source={m['source']} windows={len(m['windows'])} sheets={len(m['sheets'])}")
        for s_ in m["sheets"]:
            print("  sheet:", s_)
        print("  label stub:", stub)
    elif a.cmd == "finalize":
        doc = pipeline.finalize(a.video_id)
        print(f"{a.video_id}: {len(doc['segments'])} segments -> outputs/{a.video_id}.md")
    elif a.cmd == "learn":
        res = run_learn()
        print(f"learned from {res['corpus']['n_videos']} videos -> outputs/learned_rules.yaml, SUMMARY.md")
    elif a.cmd == "analyze":
        import glob as _glob, os as _os
        from .features import compute_for_video
        from . import pipeline as _pl
        if a.video_id:
            vids = [a.video_id]
        else:
            vids = sorted(p.split("/")[-1][:-len(".timeline.json")]
                          for p in _glob.glob(_os.path.join(_pl.OUT, "*.timeline.json")))
        for i, v in enumerate(vids, 1):
            try:
                f = compute_for_video(v, _pl.WORK, do_ocr=not a.no_ocr)
                print(f"[{i}/{len(vids)}] {v}: features for {len(f)} windows")
            except Exception as e:
                print(f"[{i}/{len(vids)}] {v}: FAILED {e}")
    elif a.cmd == "build-db":
        from .database import build
        res = build()
        print(f"database: {res['videos']} videos, {res['windows']} windows "
              f"(clean/action-only: {res['clean_windows']}); "
              f"filtered={res['filtered']}; validation_flags={res['flagged']} -> {res['dir']}")
    elif a.cmd == "prompt":
        print(CLASSIFY_PROMPT + prompt_label_reference(load_taxonomy()))


if __name__ == "__main__":
    main()
