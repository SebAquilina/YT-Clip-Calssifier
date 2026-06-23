#!/bin/bash
cd "/home/user/YT-Clip-Calssifier/video8b_veo/Project files"
export LABS69_API_KEY="vk_kokHYuBcZneKXXNZGaMzf3caxONeY3Wr"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124"
while true; do
  while pgrep -f 'python3 generate.py' >/dev/null; do sleep 15; done
  REM=$(python3 -c "import json;s=json.load(open('state.json'));M=json.load(open('manifest.json'));print(sum(1 for b in M['beats'] if s['beats'].get(b['id'],{}).get('job',{}).get('status')!='downloaded'))" 2>/dev/null)
  echo "[finish] gen ended remaining=$REM $(date -u +%H:%M)" >> finish.log
  [ "${REM:-1}" -eq 0 ] && break
  while true; do C=$(curl -s -m15 -A "$UA" "https://69labs.vip/api/v1/videos/models" -H "Authorization: Bearer $LABS69_API_KEY"|python3 -c "import sys,json;print(json.load(sys.stdin)['credits']['remaining'])" 2>/dev/null); [ "${C:-0}" -ge 40 ] 2>/dev/null && break; sleep 120; done
  echo "[finish] resuming ($REM left)" >> finish.log; python3 generate.py >> gen.log 2>&1
done
echo "[finish] assembling" >> finish.log; python3 assemble.py >> asm.log 2>&1
echo "[finish] VIDEO8B ASSEMBLED" >> finish.log
