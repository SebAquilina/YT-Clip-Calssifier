#!/bin/bash
cd "/home/user/YT-Clip-Calssifier/video4_veo/Project files"
export LABS69_API_KEY="vk_kokHYuBcZneKXXNZGaMzf3caxONeY3Wr"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124"
# wait for gen to finish; if it stalls on quota, resume after credit refresh
while true; do
  while pgrep -f 'python3 generate.py' >/dev/null; do sleep 15; done
  # count remaining
  REM=$(python3 - <<'PY'
import json
s=json.load(open("state.json")); M=json.load(open("manifest.json"))
r=0
for b in M["beats"]:
    n=s["beats"].get(b["id"],{}).get("n_clips",1)
    for i in range(n):
        if s["beats"].get(b["id"],{}).get("jobs",{}).get(str(i),{}).get("status")!="downloaded": r+=1
print(r)
PY
)
  echo "[finish] gen ended, remaining=$REM $(date -u +%H:%M)" >> finish.log
  if [ "${REM:-1}" -eq 0 ]; then break; fi
  # remaining clips -> wait for credits then resume
  while true; do
    C=$(curl -s -m15 -A "$UA" "https://69labs.vip/api/v1/videos/models" -H "Authorization: Bearer $LABS69_API_KEY"|python3 -c "import sys,json;print(json.load(sys.stdin)['credits']['remaining'])" 2>/dev/null)
    [ "${C:-0}" -ge 40 ] 2>/dev/null && break
    sleep 120
  done
  echo "[finish] resuming gen for $REM clips" >> finish.log
  python3 generate.py >> gen.log 2>&1
done
echo "[finish] all clips done -> assembling" >> finish.log
python3 assemble.py >> asm.log 2>&1
echo "[finish] VIDEO4 ASSEMBLED" >> finish.log
