"""One-time backfill: add niche terminology to existing corpus/db descriptions.

Records and the built db were written before config/vocab.yaml existed, so their
`description_detailed` don't yet name terms like tunneling / sinkhole / repour. This
walks every window, detects the terms its description implies (by surface form OR visual
cue, via enrich._terms_in), and appends a "Terminology: <terms>." clause if not already
present — idempotent (re-running adds nothing). Then it rebuilds the shared-store views.

Usage:
    python -m ytclip.vocab_backfill --store outputs/shared_db [--niche candle_making] [--dry-run]
"""
from __future__ import annotations

import argparse
import glob
import json
import os

from .enrich import _load_vocab, _terms_in

_MARK = "Terminology:"


def _augment(text: str, vocab) -> tuple[str, list]:
    if not text or _MARK in text:
        return text, []
    terms = [t.replace("_", " ") for t in _terms_in(text, vocab)
             if t.replace("_", " ") not in text.lower()]
    if not terms:
        return text, []
    return text.rstrip(". ") + f". {_MARK} " + ", ".join(terms) + ".", terms


def backfill_store(store: str, niche: str = "candle_making", dry_run: bool = False) -> dict:
    vocab = _load_vocab(niche)
    if not vocab:
        return {"error": f"no vocab for niche {niche!r}"}
    recs = sorted(glob.glob(os.path.join(store, "records", "*.json")))
    changed_windows = 0
    changed_records = 0
    from collections import Counter
    term_counts: Counter = Counter()
    for p in recs:
        rec = json.load(open(p))
        touched = False
        for w in rec.get("windows", []):
            base = w.get("description_detailed") or w.get("description") or ""
            new, terms = _augment(base, vocab)
            if terms:
                w["description_detailed"] = new
                changed_windows += 1
                touched = True
                term_counts.update(terms)
        if touched:
            changed_records += 1
            if not dry_run:
                tmp = p + ".tmp"
                with open(tmp, "w") as f:
                    json.dump(rec, f)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, p)
    result = {"records": len(recs), "records_changed": changed_records,
              "windows_changed": changed_windows, "terms": dict(term_counts.most_common()),
              "dry_run": dry_run}
    if not dry_run and changed_records:
        from . import shared_db
        result["rebuilt"] = shared_db.rebuild_views(store)["videos"]
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(prog="ytclip.vocab_backfill")
    ap.add_argument("--store", default="outputs/shared_db")
    ap.add_argument("--niche", default="candle_making")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    res = backfill_store(a.store, a.niche, a.dry_run)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
