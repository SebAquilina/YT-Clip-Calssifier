"""Footage selection — turn the vetted shared store into an assembly-ready shotlist.

Given a niche, this picks the best *usable* (clean, non-flagged) action clips for
each step of the canonical procedure, in order, deduped for variety, ready for the
normal video-making process to assemble. Talking-head / on-screen-text windows can
never appear here: they are excluded twice over by `shared_db.usable_clips`.

The step order and per-step target durations come from the learned rules
(`outputs/learned_rules.yaml`), falling back to whatever action labels are present.
"""
from __future__ import annotations

import json
import os

from . import shared_db

ROOT = shared_db.ROOT
RULES = os.path.join(ROOT, "outputs", "learned_rules.yaml")
SHOTLIST_DIR = os.path.join(ROOT, "outputs", "shotlists")


def _canonical_order(root: str | None = None, records: list | None = None) -> list:
    """Preferred step order: learned canonical order, else labels present in the store."""
    try:
        import yaml
        with open(RULES) as f:
            order = yaml.safe_load(f).get("derived_canonical_order") or []
        if order:
            return order
    except Exception:
        pass
    return shared_db._action_labels(root=root, records=records)


def _target_durations() -> dict:
    try:
        import yaml
        with open(RULES) as f:
            dur = yaml.safe_load(f).get("observed_duration_s") or {}
        return {k: (v.get("median") or v.get("mean")) for k, v in dur.items()}
    except Exception:
        return {}


def _score(clip: dict, target_s: float | None) -> float:
    """Higher = better: confident, well-grounded, near the typical step length."""
    conf = float(clip.get("confidence") or 0.0)
    dur = float(clip.get("duration_s") or 0.0)
    grounded = min(len(clip.get("description_detailed") or clip.get("description") or ""), 240) / 240.0
    fit = 0.0
    if target_s:
        fit = -0.04 * abs(dur - target_s)        # gentle penalty for being off-length
    return conf + 0.15 * grounded + fit


def build_shotlist(niche: str | None = None, order: list | None = None,
                   per_step: int = 3, max_per_video: int = 1,
                   root: str | None = None) -> dict:
    """Build a step-ordered shotlist of vetted clips for `niche`.

    per_step      how many candidate clips to offer per step
    max_per_video cap clips from the same source video per step (variety)
    """
    recs = shared_db.all_records(root)
    order = order or _canonical_order(root, records=recs)
    targets = _target_durations()
    steps = []
    total = 0
    for label in order:
        cands = shared_db.usable_clips(label=label, niche=niche, records=recs)
        cands.sort(key=lambda c: _score(c, targets.get(label)), reverse=True)
        picked, per_vid = [], {}
        for c in cands:
            vid = c.get("video_id")
            if per_vid.get(vid, 0) >= max_per_video:
                continue
            per_vid[vid] = per_vid.get(vid, 0) + 1
            picked.append({
                "video_id": vid,
                "window_index": c.get("window_index"),
                "start_s": c.get("start_s"),
                "end_s": c.get("end_s"),
                "duration_s": c.get("duration_s"),
                "confidence": c.get("confidence"),
                "clip_url": c.get("window_url"),
                "video_title": c.get("video_title"),
                "description": c.get("description_detailed") or c.get("description"),
            })
            if len(picked) >= per_step:
                break
        steps.append({"label": label, "n_available": len(cands), "clips": picked})
        total += len(picked)
    return {"niche": niche or "(all)", "order": order,
            "n_steps": len(steps), "n_clips": total, "steps": steps}


def render_markdown(shotlist: dict) -> str:
    out = [f"# Shotlist — niche: {shotlist['niche']}",
           f"_{shotlist['n_clips']} vetted clips across {shotlist['n_steps']} steps "
           f"(talking-head / on-screen-text excluded)._", ""]
    for i, step in enumerate(shotlist["steps"], 1):
        out.append(f"## {i}. {step['label']}  ({step['n_available']} available)")
        if not step["clips"]:
            out.append("_no vetted footage yet — research more videos for this step_")
        for c in step["clips"]:
            out.append(f"- **{c['clip_url']}**  ({c['duration_s']}s, conf {c['confidence']})")
            if c.get("description"):
                out.append(f"  - {c['description']}")
        out.append("")
    return "\n".join(out)


def write_shotlist(niche: str | None = None, **kw) -> dict:
    """Build and persist a shotlist to outputs/shotlists/<niche>.{json,md}."""
    sl = build_shotlist(niche=niche, **kw)
    os.makedirs(SHOTLIST_DIR, exist_ok=True)
    name = shared_db._safe(niche or "all")
    jp = os.path.join(SHOTLIST_DIR, f"{name}.json")
    mp = os.path.join(SHOTLIST_DIR, f"{name}.md")
    with open(jp, "w") as f:
        json.dump(sl, f, indent=1)
    with open(mp, "w") as f:
        f.write(render_markdown(sl))
    sl["_paths"] = {"json": jp, "md": mp}
    return sl
