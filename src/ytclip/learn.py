"""Aggregate finalized timelines into empirically-learned rules.

Reads every outputs/<vid>.timeline.json and computes, across the corpus:
  * observed mean position (0-1) of each label  -> refines typical_position
  * observed mean/median duration of each step  -> refines typical_duration
  * transition frequencies between consecutive segment labels
  * how often each step appears (coverage)

Writes outputs/learned_rules.yaml (mergeable back into config) and
outputs/SUMMARY.md. This is the "learn rules and see how they extrapolate" step.
"""
from __future__ import annotations

import glob
import json
import os
from collections import Counter, defaultdict
from statistics import mean, median

import yaml

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "outputs")
OUT = os.path.abspath(OUT)


def _load_timelines():
    docs = []
    for p in sorted(glob.glob(os.path.join(OUT, "*.timeline.json"))):
        with open(p) as f:
            docs.append(json.load(f))
    return docs


def learn() -> dict:
    docs = _load_timelines()
    positions = defaultdict(list)
    step_durations = defaultdict(list)
    transitions = Counter()
    coverage = Counter()
    n_videos = len(docs)

    for d in docs:
        dur = d["duration"] or 1
        seen = set()
        for seg in d["segments"]:
            mid = (seg["start"] + seg["end"]) / 2
            positions[seg["label"]].append(mid / dur)
            if seg["is_step"]:
                step_durations[seg["label"]].append(seg["end"] - seg["start"])
            seen.add(seg["label"])
        segs = d["segments"]
        for a, b in zip(segs, segs[1:]):
            transitions[(a["label"], b["label"])] += 1
        for lbl in seen:
            coverage[lbl] += 1

    learned = {
        "corpus": {"n_videos": n_videos,
                   "video_ids": [d["video_id"] for d in docs]},
        "observed_position": {k: round(mean(v), 3) for k, v in sorted(positions.items())},
        "observed_duration_s": {
            k: {"mean": round(mean(v), 1), "median": round(median(v), 1), "n": len(v)}
            for k, v in sorted(step_durations.items())},
        "coverage_videos": {k: coverage[k] for k in sorted(coverage)},
        "top_transitions": [
            {"from": a, "to": b, "count": c}
            for (a, b), c in transitions.most_common(20)],
        "derived_canonical_order": [
            k for k, _ in sorted(
                {k: mean(v) for k, v in positions.items()
                 if k in {s["label"] for d in docs for s in d["segments"] if s["is_step"]}}.items(),
                key=lambda kv: kv[1])],
    }

    with open(os.path.join(OUT, "learned_rules.yaml"), "w") as f:
        yaml.safe_dump(learned, f, sort_keys=False, default_flow_style=False)
    _write_summary(docs, learned)
    return learned


def _write_summary(docs, learned):
    lines = ["# Corpus summary — learned candle-DIY rules", "",
             f"Aggregated from **{learned['corpus']['n_videos']} videos**.", "",
             "## Derived canonical step order (by observed mean position)", ""]
    for i, k in enumerate(learned["derived_canonical_order"], 1):
        pos = learned["observed_position"].get(k)
        lines.append(f"{i}. `{k}`  (mean position {pos})")

    lines += ["", "## Step durations (seconds)", "",
              "| Step | mean | median | n |", "|------|-----:|-------:|--:|"]
    for k, v in learned["observed_duration_s"].items():
        lines.append(f"| `{k}` | {v['mean']} | {v['median']} | {v['n']} |")

    lines += ["", "## Step coverage (videos containing the step)", "",
              "| Label | videos |", "|-------|------:|"]
    for k, c in sorted(learned["coverage_videos"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {c}/{learned['corpus']['n_videos']} |")

    lines += ["", "## Most common transitions", "",
              "| From | To | count |", "|------|----|------:|"]
    for t in learned["top_transitions"]:
        lines.append(f"| `{t['from']}` | `{t['to']}` | {t['count']} |")

    lines += ["", "## Per-video index", ""]
    for d in docs:
        lines.append(f"- [{d['title']}]({d['url']}) — `{d['video_id']}.md` "
                     f"({len(d['segments'])} segments, source: {d['source']})")

    with open(os.path.join(OUT, "SUMMARY.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
