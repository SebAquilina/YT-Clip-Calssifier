#!/usr/bin/env python3
"""thumbs_from_xlsx.py <xlsx> "<title substring>" <out.json>
Pull the three thumbnail NANO PROMPTs (columns 'Thumbnail A/B/C') for a video into a prompts.json
that gen_thumbs.py consumes (2 variants @2k each). Strips the leading '[hook] label' line and the
'NANO PROMPT:' label so only the prompt text is sent."""
import sys, json, re, openpyxl
xlsx, title, out = sys.argv[1], sys.argv[2], sys.argv[3]
wb=openpyxl.load_workbook(xlsx, data_only=True); ws=wb["Make order (easiest first)"]
rows=list(ws.iter_rows(values_only=True)); hdr=rows[0]
ti=next(i for i,h in enumerate(hdr) if h and "Proposed Title" in str(h))
cols={L:next(i for i,h in enumerate(hdr) if h and f"Thumbnail {L}" in str(h)) for L in ("A","B","C")}
row=next((r for r in rows[1:] if r[ti] and title.lower() in str(r[ti]).lower()), None)
if not row: raise SystemExit(f"no row for title {title!r}")
def clean(cell):
    t=str(cell or "");
    m=re.search(r"NANO PROMPT:\s*(.+)", t, re.S)
    return (m.group(1) if m else t).strip()
labels={"A":"A","B":"B","C":"C"}
out_list=[{"label":f"{L}", "prompt":clean(row[cols[L]])} for L in ("A","B","C") if row[cols[L]]]
json.dump(out_list, open(out,"w"), indent=2)
print(f"wrote {out}: {len(out_list)} thumbnail prompts")
