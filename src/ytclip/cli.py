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

For EACH window tile, choose exactly ONE label from the taxonomy below that best
describes what is happening. Use visual cues; if a tile has on-screen step text,
use it. Output a JSON array, one object per window:
  {"window": <int>, "label": "<id>", "confidence": 0.0-1.0, "evidence": "<short>"}

Labels:
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
    elif a.cmd == "build-db":
        from .database import build
        res = build()
        print(f"database: {res['videos']} videos, {res['windows']} windows -> {res['dir']}")
    elif a.cmd == "prompt":
        print(CLASSIFY_PROMPT + prompt_label_reference(load_taxonomy()))


if __name__ == "__main__":
    main()
