#!/usr/bin/env bash
# make_video.sh — end-to-end driver for one video, AFTER the build script is authored.
# Usage:
#   LABS69_API_KEY=vk_...  IDEATE_XLSX=/path/ideate.xlsx \
#   bash make_video.sh <build_script.py> <project_dir> "<title substring>"
# Does: build -> script_lint (HARD GATE) -> subject agents -> generate (resumable) -> face/trunc gates
#       -> assemble -> master -> chapters+description -> tags -> thumbnails -> deliverable zip -> ~/Desktop
set -uo pipefail
BUILD="$1"; PROJ="$2"; TITLE="$3"
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"            # repo root (…/skills/ai-broll-video-maker/scripts -> root)
ENG="$ROOT/video_dollartree_build"; SK="$ROOT/skills/ai-broll-video-maker/scripts"
: "${LABS69_API_KEY:?set LABS69_API_KEY}"; : "${IDEATE_XLSX:?set IDEATE_XLSX to the ideation xlsx path}"
echo "$LABS69_API_KEY" > /tmp/apikey.txt
cd "$ROOT"; PF="$PROJ/Project files"; say(){ echo "[$(date -u +%H:%M:%S)] $*"; }

say "1/10 build script -> manifest"; python3 "$BUILD" || exit 1
say "2/10 script_lint (content blueprint + Yoder retention) — HARD GATE"
python3 "$ENG/script_lint.py" "$PROJ" --xlsx "$IDEATE_XLSX" --title "$TITLE" || { echo "LINT FAILED — fix the script"; exit 2; }
say "3/10 subject continuity agents (LLM if ANTHROPIC_API_KEY, else heuristic)"; python3 "$ENG/subject_agents.py" "$PROJ" || true

say "4/10 generate (resumable; up to 60 passes through API congestion)"
done_check(){ python3 - "$PROJ" <<'PY'
import json,os,sys,subprocess
P=sys.argv[1];PF=P+"/Project files";M=json.load(open(PF+"/manifest.json"));S=json.load(open(PF+"/state.json")) if os.path.exists(PF+"/state.json") else {"beats":{}}
def have(p):return bool(p and os.path.exists(p) and os.path.getsize(p)>2000)
def vok(p):
 if not have(p):return False
 try:return float(subprocess.run(["/usr/local/bin/ffprobe","-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip())>0.4
 except:return False
miss=[]
for b in M["beats"]:
 vm=b["visual_mode"];e=S["beats"].get(b["id"],{})
 ok=((vm=="talking_head" and vok(e.get("clip"))) or (vm=="image_split" and vok(e.get("clip")) and have(e.get("image"))) or (vm=="image_full" and have(e.get("image")) and have(e.get("audio"))) or (vm=="image_live" and vok(e.get("clip")) and have(e.get("audio"))) or (vm=="broll" and vok(e.get("clip")) and have(e.get("audio"))))
 if not ok:miss.append(b["id"])
print(len(miss)); sys.exit(0 if not miss else 1)
PY
}
for pass in $(seq 1 60); do
  if done_check >/dev/null 2>&1; then say "  all assets complete (pass $pass)"; break; fi
  say "  gen pass $pass ($(done_check 2>/dev/null) beats missing)"
  python3 "$ENG/gen_dt_par.py" "$PROJ" --vid 3 --img 4 --tts 2 >/tmp/mk_gen.log 2>&1 || true
  sleep 20
done

say "5/10 gates: face imposter + truncation/lead-in/muted"
IDS=$(python3 -c "import json;M=json.load(open('$PF/manifest.json'));print(','.join(b['id'] for b in M['beats'] if b['visual_mode'] in('talking_head','image_split')))")
[ -f /tmp/_ref_full.jpg ] || curl -sL "$(cat /tmp/raw_ref.txt 2>/dev/null)" -o /tmp/_ref_full.jpg 2>/dev/null || true
python3 "$ENG/face_check_ids.py" "$PROJ" "$IDS" 2>/dev/null || say "  (face gate flagged — review)"
python3 "$ENG/trunc_check.py" "$PROJ" 2>/dev/null | tail -3 || true

say "6/10 assemble (grok TH 10s + faster-TH + grain) + master to -16 LUFS"
python3 "$ENG/asm_dt.py" "$PROJ" "$PROJ/FINAL.mp4" >/tmp/mk_asm.log 2>&1 || { echo "assemble failed"; tail -5 /tmp/mk_asm.log; exit 3; }
python3 "$SK/master_audio.py" "$PROJ/FINAL.mp4" "$PROJ/FINAL_mastered.mp4" >>/tmp/mk_asm.log 2>&1 || cp "$PROJ/FINAL.mp4" "$PROJ/FINAL_mastered.mp4"

say "7/10 description (blueprint teaser + chapters) + tags"
HOOKW=$(python3 -c "import re;print(' '.join([w for w in re.findall(r'[A-Za-z]+','$TITLE')][:5]))")
python3 "$ENG/chapters_gen.py" "$PROJ" "$BUILD" "$TITLE" > /tmp/mk_chaps.txt 2>/dev/null || true
python3 - "$PROJ" "$IDEATE_XLSX" "$TITLE" <<'PY'
import sys,os; sys.path.insert(0,"video_dollartree_build"); import blueprint_parse as BP
proj,xlsx,title=sys.argv[1],sys.argv[2],sys.argv[3]
F=BP.parse(BP.from_xlsx(xlsx,title)); d=proj+"/description.txt"
chaps=open("/tmp/mk_chaps.txt").read().strip() if os.path.exists("/tmp/mk_chaps.txt") else ""
if not os.path.exists(d):
  body=" ".join(F["must_cover"])
  open(d,"w").write(f"Everything in this video is in my $3 ebook: \U0001F517 https://candicescandles.com\n\n{body}\n\n⏱️ Chapters\n{chaps}\n\nSubscribe for more — the next video is on screen at the end!\n\n#candles #candlemaking #diy #candice\n")
else:
  t=open(d).read()
  if chaps and "⏱" in t:
    import re; t=re.sub(r"⏱️ Chapters\n(?:[0-9].*\n?)+", "⏱️ Chapters\n"+chaps+"\n", t)
    open(d,"w").write(t)
print("description ready")
PY
python3 "$ENG/gen_tags.py" "$PROJ" "$TITLE, candle making, $HOOKW" >/dev/null 2>&1 || true

say "8/10 thumbnails (2 variants x 3 prompts @2k)"
python3 "$SK/thumbs_from_xlsx.py" "$IDEATE_XLSX" "$TITLE" /tmp/mk_thumbs.json 2>/dev/null && \
  python3 "$ENG/gen_thumbs.py" "$PROJ" /tmp/mk_thumbs.json >/tmp/mk_thumbs.log 2>&1 || say "  (thumbnails skipped/failed — review)"
cp "$PROJ"/thumbnails/*A*v1*.png "$PROJ/thumbnail.png" 2>/dev/null || true

say "9/10 package deliverable zip (+ host)"
python3 "$SK/build_deliverable.py" "$PROJ" --title "$TITLE" --host >/tmp/mk_pkg.log 2>&1 || true
grep -E "LINK:|DELIVERABLE:" /tmp/mk_pkg.log || true
ZIP=$(ls -t "$PROJ"/*_deliverable.zip 2>/dev/null | head -1)

say "10/10 save to Desktop"
DESK="$HOME/Desktop"; mkdir -p "$DESK"
cp "$PROJ/FINAL_mastered.mp4" "$DESK/${TITLE}.mp4" 2>/dev/null && say "  -> $DESK/${TITLE}.mp4"
[ -n "${ZIP:-}" ] && cp "$ZIP" "$DESK/" 2>/dev/null && say "  -> $DESK/$(basename "$ZIP")"
say "DONE: $TITLE  ($(/usr/local/bin/ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$PROJ/FINAL_mastered.mp4" 2>/dev/null)s)"
