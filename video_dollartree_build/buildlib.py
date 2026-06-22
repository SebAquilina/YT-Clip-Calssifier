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
def th(s, scene="bench", moved=False, book_cta=False, adj_ok=False):
    # adj_ok=True: this TH is allowed to sit next to another TH (ONLY in hook / outro). Even then,
    # finalize() requires the adjacent THs to be in DIFFERENT scenes (no jarring same-scene cut) and
    # the assembler crops dead silence + crossfades so there is no gap. Body THs must never be adjacent.
    _short(s)
    b={"id":_id("th"),"type":"character","visual_mode":"talking_head","sentence":s,
       "seed":K.SCENES[scene],"prompt":K.th_prompt(s,scene,moved),"scene":scene,"adj_ok":adj_ok}
    if book_cta: b["book_cta"]=True
    _B.append(b)
def book(s, scene="shelf"):
    """talking-head ebook CTA beat — real book cover gets composited by the assembler.
    Tagged c_th so the one allowed hook->CTA adjacency passes the no-adjacent-TH rule."""
    _short(s)
    _B.append({"id":_id("c_th"),"type":"character","visual_mode":"talking_head","sentence":s,
               "seed":K.SCENES[scene],"prompt":K.th_prompt(s,scene),"book_cta":True,"scene":scene,"adj_ok":True})
def full(subject, narration, shot="close-up", kb="in", subj=None):
    # subj = a subject key (e.g. "hero_candle"). The FIRST beat with a key is the canonical render;
    # later beats with the same key get that render fed in as an img2img reference so the object stays
    # identical across shots (different setting / lit / angle). See gen_dt_par subject-ref pass.
    _short(narration, 20)
    b={"id":_id("full"),"type":"image","visual_mode":"image_full","sentence":narration,
       "image_prompt":K.image_prompt(subject,shot),"kenburns":{"dir":kb},"narration":narration}
    if subj: b["subject_key"]=subj
    _B.append(b)
def split(sentence, subject, scene="bench", th_side="left", shot="close-up", subj=None):
    _short(sentence)
    b={"id":_id("split"),"type":"image","visual_mode":"image_split","sentence":sentence,
       "seed":K.SCENES[scene],"prompt":K.th_prompt(sentence,scene),"image_prompt":K.image_prompt(subject,shot),
       "ar":"1:1","split":{"th_side":th_side,"th_frac":0.46}}
    if subj: b["subject_key"]=subj
    _B.append(b)
def live(subject, motion, narration, shot="macro", subj=None):
    _short(narration, 20)
    b={"id":_id("live"),"type":"image","visual_mode":"image_live","sentence":narration,
       "image_prompt":K.image_prompt(subject,shot),"motion":motion,"narration":narration}
    if subj: b["subject_key"]=subj
    _B.append(b)
NO_MAKING_OVERRIDE=None  # b-roll already forbids spawning via K.PHONE/NOSPAWN
def br(action, narration):
    _short(narration, 20)
    pr=(f"Close-up POV iPhone shot of ONLY the hands and forearms of a mid-fifties woman (fair naturally-aged skin, "
        f"plain wedding band, blue sweater cuffs, tan apron) as she {action}. {K.NOSPAWN} Her hands ONLY — absolutely "
        f"NO face, NO head, NO other person. {K.PHONE} {K.NOTEXT} Setting: {K.WS}")
    _B.append({"id":_id("br"),"type":"broll","visual_mode":"broll","narration":narration,"prompt":pr,"broll_ref":K.HANDS})
def finalize(folder):
    # HARD RULE (v6.3): outside the hook/CTA/outro a talking head is a SINGLE 8s beat — never adjacent.
    # Adjacent THs are allowed ONLY where every beat in the run opted in (adj_ok / book CTA), AND each
    # consecutive pair changes scene (no jarring same-scene cut). The assembler kills dead silence and
    # crossfades into the next beat so adjacency has no gap and no clipped speech.
    runs=[]; run=[]
    for b in _B+[{"visual_mode":"_end","id":"_"}]:
        if b["visual_mode"]=="talking_head": run.append(b)
        else:
            if len(run)>=2: runs.append(run[:])
            run=[]
    bad_adj=[]; bad_scene=[]
    for r in runs:
        if not all(b.get("adj_ok") or b.get("book_cta") for b in r):
            bad_adj.append([b["id"] for b in r]); continue
        for a,b in zip(r,r[1:]):
            if a.get("scene")==b.get("scene"): bad_scene.append((a["id"],b["id"]))
    assert not bad_adj, f"ADJACENT TALKING-HEADS in the body (forbidden — alternate with image/VO): {bad_adj}"
    assert not bad_scene, f"ADJACENT THs must CHANGE SCENE (v6.3): {bad_scene}"
    M={"title":_meta["title"],"channel":_meta["channel"],"beats":_B}
    os.makedirs(os.path.join(folder,"Project files"),exist_ok=True)
    json.dump(M,open(os.path.join(folder,"Project files","manifest.json"),"w"),indent=2)
    c=Counter(b["visual_mode"] for b in _B); n=len(_B)
    def est(b):
        if b["visual_mode"]=="talking_head": return 7.0
        if b["visual_mode"]=="image_split": return 7.0
        w=len(b.get("narration","").split()); return max(3.0,w/3.0+0.5)
    secs=sum(est(b) for b in _B)
    pct={k:c[k]/n*100 for k in c}
    print(f"{M['title']}\n  {n} beats | mix: {dict(c)}")
    # v6.3 target mix: still 49.3 / video-clip(full) 27.7 / TH 12.3 / split+still 9.7 / split+clip 1.0
    print(f"  TH {pct.get('talking_head',0):.0f}%  full(still) {pct.get('image_full',0):.0f}%  "
          f"live+broll(clip) {pct.get('image_live',0)+pct.get('broll',0):.0f}%  split {pct.get('image_split',0):.0f}%  "
          f"| est {secs/60:.1f} min")
    if pct.get('talking_head',0)>16: print(f"  ** WARNING: TH share {pct['talking_head']:.0f}% > ~12% target **")
