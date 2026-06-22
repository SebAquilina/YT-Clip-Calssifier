#!/usr/bin/env python3
"""gen_tags.py <project_dir> "<specific,tags,for,this,video>"   (v6.4)
Write YouTube tags as a CSV line into <project_dir>/tags.txt (same idea as description.txt — a plain
text doc the user pastes into YouTube's Tags box). Tags help discovery, so we mix:
  - SPECIFIC tags for THIS video (passed in: e.g. "floating water candle, water candle diy")
  - BROAD evergreen + cross-platform tags from COMMON below (diy, candlemaking, tiktok, ...)
De-duplicates (case-insensitive), preserves order (specific first), and caps the total at YouTube's
~500-character limit. Every video gets its own file with its own specific tags."""
import os, sys
COMMON=["candles","candle making","candlemaking","diy","diy candles","how to make candles","soy candles",
"candle tutorial","candle hacks","homemade candles","home decor","crafts","candle diy","candle lover",
"candice","candices country candles","candle making for beginners","tiktok","reels","shorts","satisfying",
"oddly satisfying","asmr","cozy","handmade"]
def main():
    if len(sys.argv)<3:
        print('usage: gen_tags.py <project_dir> "specific,tags,here"'); sys.exit(1)
    proj=sys.argv[1].rstrip("/"); specific=[t.strip() for t in sys.argv[2].split(",") if t.strip()]
    out=[]; seen=set(); total=0
    for t in specific+COMMON:
        k=t.lower()
        if k in seen: continue
        add=len(t)+(1 if out else 0)
        if total+add>500: break       # YouTube tags box is ~500 chars
        out.append(t); seen.add(k); total+=add
    path=os.path.join(proj,"tags.txt")
    open(path,"w").write(",".join(out)+"\n")
    print(f"wrote {path}: {len(out)} tags, {total} chars"); print(",".join(out))
if __name__=="__main__": main()
