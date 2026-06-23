#!/usr/bin/env python3
"""blueprint_parse.py — read a video's CONTENT blueprint from the ideation xlsx (the 'Script Blueprint'
cell) into structured fields the author writes to and script_lint.py enforces.

Blueprint cell format (per row):
  TARGET LENGTH: ...
  SOURCE READ — ...
  1) INTRO HOOK — ...: <hook line>
  2) EBOOK CTA — ...: <ebook topic>
  3) SCRIPT MUST COVER (..., in order):
     • topic
  4) RETENTION & PSYCHOLOGY ...:
     • LABEL (timing): note
  5) OUTRO — ...

Usage:
  from blueprint_parse import from_xlsx, parse
  bp = from_xlsx("ideate.xlsx", "Don't Start a Candle Business")   # by title substring (or int row)
  fields = parse(bp)            # {target_length, intro_hook, ebook_topic, must_cover[], retention[], outro}
CLI: blueprint_parse.py <xlsx> "<title substring or row#>"  -> prints the blueprint + parsed fields json
"""
import re, sys, json

def _section(text, start_pat, end_pats):
    m=re.search(start_pat, text)
    if not m: return ""
    s=m.end(); e=len(text)
    for p in end_pats:
        mm=re.search(p, text[s:])
        if mm: e=min(e, s+mm.start())
    return text[s:e].strip()
def _bullets(block):
    out=[]
    for ln in block.splitlines():
        ln=ln.strip()
        if ln[:1] in ("•","-","*","·"): out.append(ln[1:].strip())
    return [b for b in out if b]

def parse(text):
    text=text or ""
    tl=re.search(r"TARGET LENGTH:\s*([^\n]+)", text)
    hook=_section(text, r"1\)\s*INTRO HOOK[^\n]*", [r"\n\s*2\)"])
    # the hook line is usually the indented line(s) after the colon header
    hook_line=" ".join(l.strip() for l in hook.splitlines() if l.strip() and not l.strip().endswith(":"))
    ebook=_section(text, r"2\)\s*EBOOK CTA[^\n]*", [r"\n\s*3\)"])
    ebook_line=" ".join(l.strip() for l in ebook.splitlines() if l.strip())
    cover=_section(text, r"3\)\s*SCRIPT MUST COVER[^\n]*", [r"\n\s*4\)"])
    retn=_section(text, r"4\)\s*RETENTION[^\n]*", [r"\n\s*5\)"])
    outro=_section(text, r"5\)\s*OUTRO[^\n]*", [r"\Z"])
    return {"target_length":(tl.group(1).strip() if tl else ""),
            "intro_hook":hook_line, "ebook_topic":ebook_line,
            "must_cover":_bullets(cover), "retention":_bullets(retn),
            "outro":" ".join(l.strip() for l in outro.splitlines() if l.strip())}

def from_xlsx(path, which, sheet="Make order (easiest first)"):
    import openpyxl
    wb=openpyxl.load_workbook(path, data_only=True); ws=wb[sheet]
    rows=list(ws.iter_rows(values_only=True)); hdr=rows[0]
    ti=next(i for i,h in enumerate(hdr) if h and "Proposed Title" in str(h))
    bi=next(i for i,h in enumerate(hdr) if h and "Script Blueprint" in str(h))
    if isinstance(which,int) or str(which).isdigit():
        return rows[int(which)][bi]
    for r in rows[1:]:
        if r[ti] and str(which).lower() in str(r[ti]).lower(): return r[bi]
    raise SystemExit(f"no row matching title {which!r}")

if __name__=="__main__":
    bp=from_xlsx(sys.argv[1], sys.argv[2])
    print("===== RAW BLUEPRINT =====\n"+str(bp)+"\n\n===== PARSED =====")
    print(json.dumps(parse(bp), indent=2, ensure_ascii=False))
