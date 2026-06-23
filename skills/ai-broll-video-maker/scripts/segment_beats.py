#!/usr/bin/env python3
"""
segment_beats.py — cut a body-segment narration into 6-9 s VISUAL BEATS.

One beat = one run of narration that should be covered by ONE generated clip.
Beats break at sentence / strong-clause boundaries, never mid-phrase, targeting
6-9 s each. Output is beats_<n>.json with the verbatim sentence per beat, which
Stage B2 turns into one iPhone B-mode Veo prompt apiece.

Word timings come from faster-whisper forced alignment when available; if it is
not installed (or --no-align is passed), timings are estimated from the script's
word count against the audio duration (good enough to plan beats; the real clip
durations are trimmed to narration in trim_and_place.py).

Usage:
  python3 segment_beats.py --audio body_1.mp3 --script body_1.md --out beats_1.json
  python3 segment_beats.py --audio body_1.mp3 --script body_1.md --out beats_1.json \
      --segment body-1 --min 6 --max 9 --no-align
"""
import argparse, json, re, sys, subprocess, os

def audio_duration(path):
    try:
        out = subprocess.run(
            ["ffprobe","-v","error","-show_entries","format=duration",
             "-of","default=nw=1:nk=1", path],
            capture_output=True, text=True, check=True).stdout.strip()
        return float(out)
    except Exception as e:
        print(f"[warn] ffprobe failed ({e}); pass --duration", file=sys.stderr)
        return None

def split_sentences(text):
    # Split into sentences, then further at strong clause boundaries (; : — , and)
    # but only when a sentence is long enough that it would overflow a beat.
    text = re.sub(r"\s+", " ", text).strip()
    sents = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sents if s.strip()]

def words_of(s):
    return [w for w in re.findall(r"\S+", s)]

def align_words(audio, script_text):
    """Return list of (word, start, end) via faster-whisper, or None."""
    try:
        from faster_whisper import WhisperModel
    except Exception:
        return None
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio, word_timestamps=True)
    words = []
    for seg in segments:
        for w in (seg.words or []):
            words.append((w.word.strip(), float(w.start), float(w.end)))
    return words or None

def estimate_words(script_text, dur):
    """Even time distribution across words when no alignment is available."""
    ws = words_of(script_text)
    if not ws or not dur:
        return None
    step = dur / len(ws)
    return [(w, i*step, (i+1)*step) for i, w in enumerate(ws)]

def beats_from_sentences(sentences, word_times, min_s, max_s):
    """Greedily pack whole sentences into beats of min_s..max_s seconds.
    Sentences longer than max_s are split at clause boundaries."""
    # Build a flat timed-word stream and a sentence->word-span index by matching
    # word order (alignment text may differ slightly; we go by order/count).
    flat = word_times
    beats, wi = [], 0
    def span_dur(a, b):
        return max(0.0, flat[b-1][2] - flat[a][1]) if b > a and b <= len(flat) else 0.0

    # token count per sentence to walk the flat stream in order
    for sent in sentences:
        n = len(words_of(sent))
        if n == 0:
            continue
        start_i = wi
        end_i = min(len(flat), wi + n)
        wi = end_i
        dur = span_dur(start_i, end_i)
        if dur <= max_s or end_i - start_i <= 1:
            beats.append({"text": sent, "wi0": start_i, "wi1": end_i})
        else:
            # split this sentence into clause chunks that each fit
            clauses = re.split(r"(?<=[;:,\u2014])\s+|\s+(?:and|but|so|then)\s+", sent)
            clauses = [c.strip() for c in clauses if c.strip()]
            ci = start_i
            for c in clauses:
                cn = len(words_of(c))
                ce = min(end_i, ci + cn)
                beats.append({"text": c, "wi0": ci, "wi1": ce})
                ci = ce
    # merge tiny adjacent beats up toward min_s
    merged = []
    for b in beats:
        if merged:
            prev = merged[-1]
            if span_dur(prev["wi0"], b["wi1"]) <= max_s and \
               span_dur(prev["wi0"], prev["wi1"]) < min_s:
                prev["text"] = (prev["text"] + " " + b["text"]).strip()
                prev["wi1"] = b["wi1"]
                continue
        merged.append(dict(b))
    out = []
    for k, b in enumerate(merged):
        a, z = b["wi0"], b["wi1"]
        if z <= a or z > len(flat):
            continue
        out.append({
            "start": round(flat[a][1], 2),
            "end": round(flat[z-1][2], 2),
            "dur": round(flat[z-1][2] - flat[a][1], 2),
            "sentence": b["text"],
        })
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--script", required=True, help="the body_<n>.md narration text")
    ap.add_argument("--out", required=True)
    ap.add_argument("--segment", default="body-?", help="segment id for the manifest")
    ap.add_argument("--min", type=float, default=6.0)
    ap.add_argument("--max", type=float, default=9.0)
    ap.add_argument("--duration", type=float, default=None)
    ap.add_argument("--no-align", action="store_true")
    args = ap.parse_args()

    script_text = open(args.script, encoding="utf-8").read()
    sentences = split_sentences(script_text)

    word_times = None
    if not args.no_align:
        word_times = align_words(args.audio, script_text)
        if word_times is None:
            print("[info] faster-whisper unavailable; estimating timings", file=sys.stderr)
    if word_times is None:
        dur = args.duration or audio_duration(args.audio)
        word_times = estimate_words(script_text, dur)
        if word_times is None:
            print("[error] could not time the narration; pass --duration", file=sys.stderr)
            sys.exit(1)

    beats = beats_from_sentences(sentences, word_times, args.min, args.max)
    for i, b in enumerate(beats, 1):
        b["id"] = f"{args.segment}-{i:02d}"
        b["segment"] = args.segment
        b["status"] = "pending"
        b["prompt"] = None
        b["anchor_keyframe"] = None
        b["chain_from"] = None
        b["file"] = None
        b["job_id"] = None

    json.dump({"segment": args.segment, "beats": beats}, open(args.out,"w"), indent=2)
    tot = sum(b["dur"] for b in beats)
    print(f"[ok] {len(beats)} beats, {tot:.1f}s total -> {args.out}")
    for b in beats:
        print(f"  {b['id']}  {b['dur']:4.1f}s  {b['sentence'][:70]}")

if __name__ == "__main__":
    main()
