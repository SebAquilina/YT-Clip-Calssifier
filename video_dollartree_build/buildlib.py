#!/usr/bin/env python3
"""buildlib.py — shared beat helpers for the image-visuals candle videos (FORMAT v5.9).
Rules enforced here: talking head ~30% (full-frame VO is the default carrier), intro/outro/CTA
are talking head, lines kept short (<=16 words; asserts), book CTA composites the real cover.
A build script does: from buildlib import *; start(title, channel); th(...)/full(...)/...; finalize(folder)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import imgkit as K
from collections import Counter
_B=[]; _n=[0]; _meta={}
def start(title, channel="Candice's Country Candles"):
    _B.clear(); _n[0]=0; _meta["title"]=title; _meta["channel"]=channel
def _id(tag): i=_n[0]; _n[0]+=1; return f"b{i:03d}_{tag}"
def _short(s, limit=17):
    assert len(s.split())<=limit, f"line too long ({len(s.split())}w, keep <= {limit}): {s!r}"
def th(s, scene="bench", moved=False, book_cta=False):
    _short(s)
    b={"id":_id("th"),"type":"character","visual_mode":"talking_head","sentence":s,
       "seed":K.SCENES[scene],"prompt":K.th_prompt(s,scene,moved)}
    if book_cta: b["book_cta"]=True
    _B.append(b)
def book(s, scene="bench"):
    """talking-head ebook CTA beat — real book cover gets composited by the assembler."""
    th(s, scene=scene, book_cta=True)
def full(subject, narration, shot="close-up", kb="in"):
    _short(narration, 20)
    _B.append({"id":_id("full"),"type":"image","visual_mode":"image_full","sentence":narration,
               "image_prompt":K.image_prompt(subject,shot),"kenburns":{"dir":kb},"narration":narration})
def split(sentence, subject, scene="bench", th_side="left", shot="close-up"):
    _short(sentence)
    _B.append({"id":_id("split"),"type":"image","visual_mode":"image_split","sentence":sentence,
               "seed":K.SCENES[scene],"prompt":K.th_prompt(sentence,scene),"image_prompt":K.image_prompt(subject,shot),
               "ar":"1:1","split":{"th_side":th_side,"th_frac":0.46}})
def live(subject, motion, narration, shot="macro"):
    _short(narration, 20)
    _B.append({"id":_id("live"),"type":"image","visual_mode":"image_live","sentence":narration,
               "image_prompt":K.image_prompt(subject,shot),"motion":motion,"narration":narration})
NO_MAKING_OVERRIDE=None  # b-roll already forbids spawning via K.PHONE/NOSPAWN
def br(action, narration):
    _short(narration, 20)
    pr=(f"Close-up POV iPhone shot of ONLY the hands and forearms of a mid-fifties woman (fair naturally-aged skin, "
        f"plain wedding band, blue sweater cuffs, tan apron) as she {action}. {K.NOSPAWN} Her hands ONLY — absolutely "
        f"NO face, NO head, NO other person. {K.PHONE} {K.NOTEXT} Setting: {K.WS}")
    _B.append({"id":_id("br"),"type":"broll","visual_mode":"broll","narration":narration,"prompt":pr,"broll_ref":K.HANDS})
def finalize(folder):
    M={"title":_meta["title"],"channel":_meta["channel"],"beats":_B}
    os.makedirs(os.path.join(folder,"Project files"),exist_ok=True)
    json.dump(M,open(os.path.join(folder,"Project files","manifest.json"),"w"),indent=2)
    c=Counter(b["visual_mode"] for b in _B); n=len(_B)
    def est(b):
        if b["visual_mode"] in("talking_head","image_split"): return 7.5
        w=len(b.get("narration","").split()); return max(3.0,w/2.7+0.6)
    secs=sum(est(b) for b in _B)
    print(f"{M['title']}\n  {n} beats | mix: {dict(c)}")
    print(f"  TH share: {c['talking_head']/n*100:.0f}%  | est runtime: {secs/60:.1f} min")
    if c['talking_head']/n>0.34: print(f"  ** WARNING: TH share {c['talking_head']/n*100:.0f}% > 30% target **")
