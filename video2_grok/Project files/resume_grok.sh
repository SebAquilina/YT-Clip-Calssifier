#!/bin/bash
cd "/home/user/YT-Clip-Calssifier/video2_grok/Project files"
export LABS69_API_KEY="vk_kokHYuBcZneKXXNZGaMzf3caxONeY3Wr"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124"
echo "[resume] $(date -u) waiting for credit reset..." >> resume.log
while true; do
  R=$(curl -s -m15 -A "$UA" "https://69labs.vip/api/v1/videos/models" -H "Authorization: Bearer $LABS69_API_KEY" | python3 -c "import sys,json;print(json.load(sys.stdin)['credits']['remaining'])" 2>/dev/null)
  echo "[resume] $(date -u +%H:%M) credits=$R" >> resume.log
  if [ "${R:-0}" -ge 60 ] 2>/dev/null; then break; fi
  sleep 120
done
echo "[resume] credits back -> generating remaining grok clips" >> resume.log
python3 generate.py >> gen.log 2>&1
echo "[resume] grok generate complete -> assembling" >> resume.log
python3 assemble.py >> asm.log 2>&1
echo "[resume] GROK COMPLETE" >> resume.log
