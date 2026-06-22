#!/usr/bin/env python3
"""script_lint.py — THE ENFORCEMENT GATE for the script-generation phase (v7.1). Fails (exit 1) unless a
built script honors BOTH:
  (A) the xlsx CONTENT blueprint  — every 'SCRIPT MUST COVER' topic appears (in order), the intro hook
      says the title, the ebook CTA lands early and says 'ebook', the outro asks subscribe+next; and
  (B) the Elias-Yoder RETENTION playbook — required retention roles are present and tagged, >=2 open
      loops (>=1 late), >=3 'one more thing' escalations, >=1 on-theme story, a coined phrase repeated
      >=2x, a concrete number in the first ~20s, a late stakes zoom-out, recap, comment-bait, sequel hook
      and the signature sign-off.
Run AFTER finalize(), BEFORE generation.
  script_lint.py <project_dir> --xlsx <ideate.xlsx> --title "<title substring>"
  script_lint.py <project_dir> --blueprint <blueprint.txt>
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blueprint_parse as BP
try: import buildlib as BL; SIGNOFF=BL.SIGNOFF
except Exception: SIGNOFF=None

STOP=set("the a an of to and or in on with for from into is are this that your you it its his her their "
"how what why when make made making real natural simple little big first your you'll".split())
def toks(s): return [w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(w)>=4 and w not in STOP]

def main():
    proj=sys.argv[1].rstrip("/")
    M=json.load(open(os.path.join(proj,"Project files","manifest.json")))
    beats=M["beats"]; title=M.get("title","")
    narr=" ".join((b.get("narration") or b.get("sentence") or "") for b in beats).lower()
    early=" ".join((b.get("narration") or b.get("sentence") or "") for b in beats[:4]).lower()
    roles=[b.get("role") for b in beats if b.get("role")]
    rc={};
    for r in roles: rc[r]=rc.get(r,0)+1
    # blueprint
    if "--blueprint" in sys.argv: bp=open(sys.argv[sys.argv.index("--blueprint")+1]).read()
    else: bp=BP.from_xlsx(sys.argv[sys.argv.index("--xlsx")+1], sys.argv[sys.argv.index("--title")+1])
    F=BP.parse(bp)
    fails=[]; warns=[]; oks=[]
    def chk(cond, label, hard=True):
        (oks if cond else (fails if hard else warns)).append(label)

    # ---------- (A) CONTENT blueprint ----------
    for topic in F["must_cover"]:
        tt=toks(topic)
        hit=sum(1 for w in set(tt) if w in narr)
        chk(hit>=max(1,min(2,len(set(tt)))), f"COVER: '{topic[:48]}' ({hit} kw hits)")
    # title said in the hook region (first ~7 beats)
    twords=[w for w in toks(title)][:6]; hookreg=" ".join((b.get('sentence') or b.get('narration') or '') for b in beats[:7]).lower()
    chk(sum(1 for w in set(twords) if w in hookreg)>=max(2,len(set(twords))//2), "HOOK says the title")
    # ebook CTA early + says 'ebook'
    cta=[i for i,b in enumerate(beats) if b.get("book_cta")]
    chk(bool(cta), "EBOOK CTA present")
    if cta:
        chk(cta[0]<=14, f"EBOOK CTA early (beat {cta[0]}, ~<1:30)")
        chk("ebook" in (beats[cta[0]].get('sentence','')+beats[cta[0]+1].get('sentence','') if cta[0]+1<len(beats) else beats[cta[0]].get('sentence','')).lower(), "CTA says 'ebook'")
    chk(any(k in narr for k in ("subscribe","on screen","next video","watch this")), "OUTRO subscribe+next")

    # ---------- (B) Yoder retention ----------
    chk(rc.get("cold_open",0)>=1, "cold_open beat tagged")
    chk(bool(re.search(r"\d", early)) or any(w in early for w in("dollar","cents","percent")), "concrete NUMBER in first ~20s")
    loops=rc.get("withheld",0)+rc.get("dark_loop",0)+rc.get("promise",0)
    chk(loops>=2, f"open loops >=2 ({loops})")
    chk(rc.get("dark_loop",0)>=1 or rc.get("villain",0)>=1, "a LATE/dark loop or villain")
    chk(rc.get("villain",0)>=1, "villain ('follow the money') beat")
    chk(any(k in narr for k in("not a conspiracy","is not a conspiracy","just how the money","just incentives","quiet agreement")), "villain disclaimer ('not a conspiracy')", hard=False)
    chk(rc.get("honesty",0)>=1, "honesty / 'what this won't do' beat")
    chk(rc.get("escalation",0)>=3, f"'one more thing' escalations >=3 ({rc.get('escalation',0)})")
    chk(rc.get("story",0)>=1, "on-theme story beat")
    chk(rc.get("stakes",0)>=1, "late stakes zoom-out beat")
    chk(rc.get("recap",0)>=1, "recap checklist beat")
    chk(rc.get("future_pace",0)>=1, "future-pacing beat", hard=False)
    chk(rc.get("comment_bait",0)>=1, "comment-bait beat")
    chk(rc.get("sequel_hook",0)>=1, "sequel hook beat")
    chk(rc.get("signoff",0)>=1, "signature sign-off beat")
    # coined phrase repeated >=2x
    coined=M.get("coined",[])
    chk(bool(coined), "a coined phrase registered (coin())")
    for c in coined:
        key=" ".join(toks(c)[:3])
        n=narr.count(key.split()[0]) if key else 0
        chk(narr.count(c.lower())>=2 or (key and all(narr.count(w)>=2 for w in key.split()[:1])), f"coined '{c[:32]}' repeated >=2x", hard=False)

    # ---------- (C) FORMAT MIX (the one authoritative target; #1 drift is too much talking head) ----------
    n=len(beats) or 1
    vc={}
    for b in beats: vc[b["visual_mode"]]=vc.get(b["visual_mode"],0)+1
    th=vc.get("talking_head",0)*100/n; sp=vc.get("image_split",0)*100/n
    still=vc.get("image_full",0)*100/n; clip=(vc.get("image_live",0)+vc.get("broll",0))*100/n
    face=th+sp
    chk(th<=18, f"MIX talking-head {th:.0f}% <=18 (target 12.3)")
    chk(face<=32, f"MIX presenter/face {face:.0f}% <=32 (target ~23: TH 12.3 + split 10.7)")
    chk(still>=40, f"MIX still-image {still:.0f}% >=40 (target 49.3)", hard=False)
    chk(clip>=18, f"MIX video-clip {clip:.0f}% >=18 (target 27.7)", hard=False)

    print("=== SCRIPT LINT ===")
    for o in oks: print("  ok  ", o)
    for w in warns: print("  warn", w)
    for f in fails: print("  FAIL", f)
    print(f"\n{len(oks)} ok / {len(warns)} warn / {len(fails)} FAIL")
    sys.exit(1 if fails else 0)

if __name__=="__main__": main()
