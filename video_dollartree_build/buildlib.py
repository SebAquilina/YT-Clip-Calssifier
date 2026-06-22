#!/usr/bin/env python3
"""buildlib.py — shared beat helpers for the image-visuals candle videos (FORMAT v5.9).
Rules enforced here: talking head ~30% (full-frame VO is the default carrier), intro/outro/CTA
are talking head, lines kept short (<=16 words; asserts), book CTA composites the real cover.
A build script does: from buildlib import *; start(title, channel); th(...)/full(...)/...; finalize(folder)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import imgkit as K
from collections import Counter
_B=[]; _n=[0]; _meta={}
# v7.1 — Elias-Yoder retention roles a script can tag beats with (script_lint enforces the required set):
RETENTION_ROLES={"cold_open","withheld","identity","dark_loop","promise","reframe","mechanism","step",
"escalation","story","honesty","villain","stakes","recap","future_pace","comment_bait","sequel_hook","signoff"}
# Candice's signature sign-off (series consistency, like Yoder's repeated closer) — say it ~verbatim every video.
SIGNOFF="Because a candle you made yourself says someone took the time, and that is the point."
def start(title, channel="Candice's Country Candles"):
    _B.clear(); _n[0]=0; _meta.clear(); _meta["title"]=title; _meta["channel"]=channel
    _meta["coined"]=[]; _meta["loops_opened"]=0
def coin(phrase):
    """Register the video's ONE coined/reframe phrase (Yoder technique #6). script_lint checks it is
    actually repeated >=2x across the narration."""
    _meta.setdefault("coined",[]).append(phrase)
def _role(b, role):
    if role:
        assert role in RETENTION_ROLES, f"unknown retention role {role!r}; use one of {sorted(RETENTION_ROLES)}"
        b["role"]=role
        if role in ("withheld","dark_loop","promise"): _meta["loops_opened"]=_meta.get("loops_opened",0)+1
    return b
def _id(tag): i=_n[0]; _n[0]+=1; return f"b{i:03d}_{tag}"
def _short(s, limit=17):
    assert len(s.split())<=limit, f"line too long ({len(s.split())}w, keep <= {limit}): {s!r}"
def th(s, scene="bench", moved=False, book_cta=False, adj_ok=False, role=None):
    # adj_ok=True: this TH is allowed to sit next to another TH (ONLY in hook / outro). Even then,
    # finalize() requires the adjacent THs to be in DIFFERENT scenes (no jarring same-scene cut) and
    # the assembler crops dead silence + crossfades so there is no gap. Body THs must never be adjacent.
    # role= tags the Yoder retention beat (cold_open / dark_loop / villain / honesty / signoff / ...).
    _short(s)
    b={"id":_id("th"),"type":"character","visual_mode":"talking_head","sentence":s,"engine":"grok",
       "seed":K.SCENES[scene],"prompt":K.grok_th_prompt(s,scene,moved),"scene":scene,"adj_ok":adj_ok}
    if book_cta: b["book_cta"]=True
    _B.append(_role(b,role))
def book(s, scene="shelf"):
    """LEGACY single-beat ebook CTA. Prefer cta_ebook() (v6.4 two-beat SOP)."""
    _short(s)
    _B.append({"id":_id("c_th"),"type":"character","visual_mode":"talking_head","sentence":s,"engine":"grok",
               "seed":K.SCENES[scene],"prompt":K.grok_th_prompt(s,scene),"book_cta":True,"scene":scene,"adj_ok":True})
def cta_ebook(line_with_ebook, line_trust, scene1="shelf", scene2="bench"):
    """v6.4 EBOOK CTA SOP — must land within the first 1:30 and is TWO talking-head beats in DIFFERENT
    scenes (Candice's keyframe is brought to life speaking; never an image/VO beat):
      Beat 1 (scene1): the REAL ebook cover is composited in; the line ties THIS video's exact topic to
        the ebook as the reason to grab it.
      Beat 2 (scene2): a TRUST line — 'it's there if you want it, I won't mention it again' + the
        why ('I'm tired of people wasting money on candles a few small cheap changes would fix').
    Always call it an EBOOK, never 'book'. Mention it ONCE, here, and never again."""
    _short(line_with_ebook); _short(line_trust)
    _B.append({"id":_id("c_th"),"type":"character","visual_mode":"talking_head","sentence":line_with_ebook,"engine":"grok",
               "seed":K.SCENES[scene1],"prompt":K.grok_th_prompt(line_with_ebook,scene1),"book_cta":True,"scene":scene1,"adj_ok":True})
    _B.append({"id":_id("c_th"),"type":"character","visual_mode":"talking_head","sentence":line_trust,"engine":"grok",
               "seed":K.SCENES[scene2],"prompt":K.grok_th_prompt(line_trust,scene2),"scene":scene2,"adj_ok":True})
def full(subject, narration, shot="close-up", kb="in", subj=None, role=None):
    # subj = an OPTIONAL explicit subject key to force a chain. Even without it, finalize() runs
    # auto_subject_refs(): it reads the script in order and, when a later image depicts the SAME evolving
    # subject as an earlier one (e.g. the candle being built step by step), it feeds the earlier render in
    # as an img2img reference so the object stays consistent (critical for DIY, where the subject evolves).
    _short(narration, 20)
    b={"id":_id("full"),"type":"image","visual_mode":"image_full","sentence":narration,
       "image_prompt":K.image_prompt(subject,shot),"kenburns":{"dir":kb},"narration":narration,"subject_text":subject}
    if subj: b["subject_key"]=subj
    _B.append(_role(b,role))
def split(sentence, subject, scene="bench", th_side="left", shot="close-up", subj=None, role=None):
    _short(sentence)
    b={"id":_id("split"),"type":"image","visual_mode":"image_split","sentence":sentence,"engine":"grok",
       "seed":K.SCENES[scene],"prompt":K.grok_th_prompt(sentence,scene),"image_prompt":K.image_prompt(subject,shot),
       "ar":"1:1","split":{"th_side":th_side,"th_frac":0.46},"subject_text":subject}
    if subj: b["subject_key"]=subj
    _B.append(_role(b,role))
def live(subject, motion, narration, shot="macro", subj=None, role=None):
    _short(narration, 20)
    b={"id":_id("live"),"type":"image","visual_mode":"image_live","sentence":narration,
       "image_prompt":K.image_prompt(subject,shot),"motion":motion,"narration":narration,"subject_text":subject}
    if subj: b["subject_key"]=subj
    _B.append(_role(b,role))
NO_MAKING_OVERRIDE=None  # b-roll already forbids spawning via K.PHONE/NOSPAWN
def br(action, narration, role=None):
    _short(narration, 20)
    pr=(f"Close-up POV iPhone shot of ONLY the hands and forearms of a mid-fifties woman (fair naturally-aged skin, "
        f"plain wedding band, blue sweater cuffs, tan apron) as she {action}. {K.NOSPAWN} Her hands ONLY — absolutely "
        f"NO face, NO head, NO other person. {K.PHONE} {K.NOTEXT} Setting: {K.WS}")
    _B.append(_role({"id":_id("br"),"type":"broll","visual_mode":"broll","narration":narration,"prompt":pr,"broll_ref":K.HANDS},role))
import re as _re
# generic words that don't identify a subject — ignored when matching one image to another
_STOP=set(("a an the of on in with and or to for from into onto over above under up down it its her his "
"their this that these those one two three five few some more most very small little big real natural "
"casual phone photo iphone closeup close macro wide shot view side angle eye level lined row beside next "
"finished fresh same different gentle soft warm cool clear plain simple beautiful gorgeous pretty nice "
"workbench bench workshop home table surface light window honest clutter around onto").split())
def _subject_nouns(t):
    # significant tokens that identify the physical subject (len>=3, not a stopword)
    return set(w for w in _re.findall(r"[a-z]+", (t or "").lower()) if len(w)>=3 and w not in _STOP)
def auto_subject_refs(min_overlap=2):
    """v6.4 — read the script IMAGE BY IMAGE and group stills that depict the SAME subject; each non-first
    member reuses the GROUP ANCHOR's render as an img2img reference (subject_ref_of), so an evolving DIY
    subject (jar -> wax poured -> cured -> lit -> gifted) keeps ONE consistent identity as it changes.
    We chain to the group ANCHOR (earliest match), not the immediate predecessor, so chains are depth-1
    stars — the anchors render first (pre-pass) and every other member then renders in parallel off the
    anchor (no deep sequential dependency). A new group is opened when an image matches no existing anchor.
    Explicit subj= keys win. The authoring agent should check a 'what NOT to do' shot didn't get grouped
    with the perfect hero (override with subj= or a distinct subject phrasing)."""
    imgs=[b for b in _B if b["visual_mode"] in ("image_full","image_live","image_split")]
    anchors=[]   # (beat, nounset) group representatives, in script order
    chained=0
    for b in imgs:
        if b.get("subject_key") or b.get("subject_ref_of"): continue
        ni=_subject_nouns(b.get("subject_text"))
        if len(ni)<2: continue
        match=next((ab for ab,an in anchors if len(ni & an)>=min_overlap), None)
        if match: b["subject_ref_of"]=match["id"]; chained+=1
        else: anchors.append((b,ni))   # this beat is a new group anchor (a chain root)
    return chained

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
    nchain=auto_subject_refs()   # v6.4: auto-detect evolving subjects -> img2img reference chains
    M={"title":_meta["title"],"channel":_meta["channel"],"beats":_B,
       "coined":_meta.get("coined",[]),"signoff":SIGNOFF}   # v7.1: retention metadata for script_lint
    os.makedirs(os.path.join(folder,"Project files"),exist_ok=True)
    json.dump(M,open(os.path.join(folder,"Project files","manifest.json"),"w"),indent=2)
    # v7.1 retention checklist (soft warnings here; script_lint.py is the hard gate vs the xlsx blueprint)
    present={b.get("role") for b in _B if b.get("role")}
    need={"cold_open","dark_loop","villain","honesty","stakes","recap","comment_bait","sequel_hook","signoff"}
    missing=need-present
    print(f"  retention roles present: {sorted(present)}")
    if missing: print(f"  ** MISSING retention roles: {sorted(missing)} (script_lint will fail) **")
    esc=sum(1 for b in _B if b.get("role")=="escalation"); loops=_meta.get("loops_opened",0)
    print(f"  open-loops: {loops} | escalations: {esc} | coined: {_meta.get('coined',[])}")
    c=Counter(b["visual_mode"] for b in _B); n=len(_B)
    def est(b):
        if b["visual_mode"]=="talking_head": return 7.0
        if b["visual_mode"]=="image_split": return 7.0
        w=len(b.get("narration","").split()); return max(3.0,w/3.0+0.5)
    secs=sum(est(b) for b in _B)
    pct={k:c[k]/n*100 for k in c}
    print(f"{M['title']}\n  {n} beats | mix: {dict(c)}")
    # ---- THE ONE AUTHORITATIVE FORMAT MIX (v7.2) — supersedes every earlier FORMAT version number ----
    # category            visual_mode(s)            target %
    #   still (full)       image_full                49.3
    #   video clip (full)  image_live + broll        27.7
    #   talking head       talking_head              12.3
    #   split (presenter)  image_split               10.7  (presenter+still 9.7 + presenter+clip 1.0)
    th=pct.get('talking_head',0); still=pct.get('image_full',0)
    clip=pct.get('image_live',0)+pct.get('broll',0); sp=pct.get('image_split',0); face=th+sp
    print(f"  MIX vs target:  still {still:.0f}/49  clip {clip:.0f}/28  TH {th:.0f}/12  split {sp:.0f}/11  "
          f"| presenter(face)={face:.0f}/23  | est {secs/60:.1f} min")
    # HARD ENFORCEMENT — the #1 drift is too much talking head. Fail the build (don't just warn) so an
    # agent can't ship a 40%-TH script. Bands are generous around the 12.3% / 23% targets.
    th_ct=c.get('talking_head',0); face_ct=th_ct+c.get('image_split',0)
    if th>18.0:
        conv=th_ct-int(0.13*n+0.5)
        raise AssertionError(f"TALKING-HEAD {th:.0f}% >> 12.3% target. Convert ~{conv} talking_head beats "
            f"to image_full/image_live VO (keep TH only for hook, ebook CTA, honesty, stakes, outro).")
    if face>32.0:
        raise AssertionError(f"PRESENTER share {face:.0f}% >> 23% target (TH {th:.0f}% + split {sp:.0f}%). "
            f"Convert some talking_head/image_split beats to image_full/image_live.")
    if th>15.0: print(f"  ** WARNING: TH {th:.0f}% above 12.3% target (ok up to ~15%) **")
    if still<40.0: print(f"  ** WARNING: still-image share {still:.0f}% below ~49% target — add image_full VO **")
    keyed=sum(1 for b in _B if b.get("subject_key"))
    print(f"  subject chains: {nchain} auto-linked + {keyed} explicit (consistency for evolving subjects)")
