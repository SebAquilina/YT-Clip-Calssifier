#!/bin/bash
# Supervisor: keep (re)launching the resumable chained generator until all 80 clips
# are downloaded. Each generate_chained.py run self-exits at its 55-min deadline; we
# relaunch to continue. Credit-cap (100/hr) safe: total work is ~91 credits, no regen.
cd "/home/user/YT-Clip-Calssifier/video_ps_veo/Project files" || exit 1
export LABS69_API_KEY=vk_kokHYuBcZneKXXNZGaMzf3caxONeY3Wr
GEN=/home/user/YT-Clip-Calssifier/skills/ai-broll-video-maker/scripts/generate_chained.py
done_count(){ python3 -c "import json;s=json.load(open('state.json'));print(sum(1 for b in s['beats'].values() if b.get('job',{}).get('status')=='downloaded'))" 2>/dev/null || echo 0; }
while true; do
  n=$(done_count)
  if [ "$n" = "80" ]; then echo "SUPERVISOR: all 80 done"; break; fi
  # wait for any existing generator to finish before relaunching
  while pgrep -f generate_chained.py >/dev/null; do sleep 20; done
  n=$(done_count)
  if [ "$n" = "80" ]; then echo "SUPERVISOR: all 80 done"; break; fi
  echo "SUPERVISOR: relaunch at $n/80 $(date -u +%H:%M:%S)"
  python3 "$GEN" >> /tmp/ps_gen.log 2>&1
  sleep 5
done