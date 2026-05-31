"""Reliable, self-verifying Google Drive sync for the shared clip corpus.

The weak link in syncing records to Drive is transcription: a human (or an LLM)
copying a multi-KB base64 blob into/out of a Drive API call can drop a character
invisibly. This module removes the human's EYES from the trust path — integrity is
decided by code (gzip CRC32 + SHA-256), and any transfer is retryable until the
checksum passes.

Protocol (the orchestrator drives the MCP create_file / download_file_content calls):

  1. `manifest`  — write records/manifest.json: per video_id the sha256 of the JSON,
     the gzip bytes (deterministic, mtime-stripped) and their sha256 + size. This is
     the source-of-truth checksum set.
  2. `b64 <id>`  — print the EXACT deterministic base64 to upload (gzip -n, so the
     bytes — and thus size+sha — are reproducible). Upload it with create_file
     (contentMimeType=application/gzip, disableConversionToGoogleType=true,
     title=<id>.json.gz), then confirm get_file_metadata.fileSize == manifest gz_bytes.
  3. `verify <id>` (stdin = the base64 the Drive download returned) — decode, check the
     gzip CRC, sha256 the inner JSON, and compare to the manifest. Exit 0 = byte-perfect,
     exit 2 = MISMATCH (re-paste / re-upload). This is the check that makes the round
     trip reliable regardless of how the bytes travelled.

Because verification is a checksum, a mistyped paste cannot pass — you simply retry.
On import, `drive.import_record` (skill) / `ingest` also rejects anything whose sha256
doesn't match the manifest, so corruption can never enter the corpus.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_STORE = os.path.join(ROOT, "outputs", "shared_db")


def _records(store):
    import glob
    return sorted(glob.glob(os.path.join(store, "records", "*.json")))


def _gz_bytes(path):
    """Deterministic gzip of a file (mtime + name stripped) so size & sha are stable."""
    raw = open(path, "rb").read()
    return gzip.compress(raw, mtime=0)


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def build_manifest(store):
    """{video_id: {bytes, sha256, gz_bytes, gz_sha256}} over all records, written to disk."""
    man = {}
    for p in _records(store):
        vid = os.path.basename(p)[:-5]
        raw = open(p, "rb").read()
        gz = gzip.compress(raw, mtime=0)
        man[vid] = {"bytes": len(raw), "sha256": _sha(raw),
                    "gz_bytes": len(gz), "gz_sha256": _sha(gz)}
    out = {"records": man, "count": len(man)}
    path = os.path.join(store, "records", "manifest.json")
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)
    return out


def load_manifest(store):
    p = os.path.join(store, "records", "manifest.json")
    return json.load(open(p)).get("records", {}) if os.path.exists(p) else {}


def b64_for(store, vid):
    import base64
    p = os.path.join(store, "records", f"{vid}.json")
    return base64.b64encode(_gz_bytes(p)).decode("ascii")


def verify_b64(store, vid, b64_text):
    """Check a (downloaded) base64 gz against the manifest. Returns (ok, detail)."""
    import base64
    man = load_manifest(store).get(vid)
    if not man:
        return False, f"no manifest entry for {vid} (run `manifest` first)"
    try:
        gz = base64.b64decode(b64_text.strip())
    except Exception as e:
        return False, f"not valid base64: {e}"
    if len(gz) != man["gz_bytes"]:
        return False, f"gz size {len(gz)} != manifest {man['gz_bytes']} (transfer truncated/garbled)"
    if _sha(gz) != man["gz_sha256"]:
        return False, "gz sha256 mismatch (bytes altered in transit)"
    try:
        raw = gzip.decompress(gz)          # also checks the gzip CRC32
    except Exception as e:
        return False, f"gzip CRC/decompress failed: {e}"
    if _sha(raw) != man["sha256"]:
        return False, "inner JSON sha256 mismatch"
    try:
        json.loads(raw)
    except Exception as e:
        return False, f"inner JSON invalid: {e}"
    return True, f"OK {vid}: {man['gz_bytes']} gz bytes, sha {man['sha256'][:12]}…"


def _cli(argv=None):
    ap = argparse.ArgumentParser(prog="ytclip.drive_sync")
    ap.add_argument("--store", default=DEFAULT_STORE)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("manifest")
    b = sub.add_parser("b64"); b.add_argument("video_id")
    v = sub.add_parser("verify"); v.add_argument("video_id")
    v.add_argument("--b64", help="base64 text (else read stdin)")
    p = sub.add_parser("plan")  # what to push: id, gz size, sha
    a = ap.parse_args(argv)

    if a.cmd == "manifest":
        m = build_manifest(a.store)
        print(json.dumps(m, indent=1))
    elif a.cmd == "b64":
        print(b64_for(a.store, a.video_id))
    elif a.cmd == "verify":
        text = a.b64 if a.b64 is not None else sys.stdin.read()
        ok, detail = verify_b64(a.store, a.video_id, text)
        print(("VERIFIED " if ok else "MISMATCH ") + detail)
        sys.exit(0 if ok else 2)
    elif a.cmd == "plan":
        man = build_manifest(a.store)["records"]
        for vid, m in sorted(man.items()):
            print(f"{vid}.json.gz  gz_bytes={m['gz_bytes']}  gz_sha256={m['gz_sha256']}")


if __name__ == "__main__":
    _cli()
