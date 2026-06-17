#!/bin/bash
# Supervisor: keep (re)launching the resumable chained generator until ALL beats are
# downloaded. Each generate_chained.py run self-exits at its ~55-min deadline; we
# relaunch to continue. Usage: run_until_done.sh [project_dir] [gen_log]
PROJ="${1:-/home/user/YT-Clip-Calssifier/video_ps_veo}"
LOG="${2:-/tmp/ps_gen.log}"
cd "$PROJ/Project files" || exit 1
export LABS69_API_KEY=vk_kokHYuBcZneKXXNZGaMzf3caxONeY3Wr
GEN=/home/user/YT-Clip-Calssifier/skills/ai-broll-video-maker/scripts/generate_chained.py
total(){ python3 -c "import json;print(len(json.load(open('manifest.json'))['beats']))" 2>/dev/null || echo 999; }
done_count(){ python3 -c "import json;s=json.load(open('state.json'));print(sum(1 for b in s['beats'].values() if b.get('job',{}).get('status')=='downloaded'))" 2>/dev/null || echo 0; }
T=$(total)
while true; do
  n=$(done_count)
  if [ "$n" -ge "$T" ]; then echo "SUPERVISOR: all $T done"; break; fi
  while pgrep -f "python3 .*generate_chained.py" >/dev/null; do sleep 20; done
  n=$(done_count)
  if [ "$n" -ge "$T" ]; then echo "SUPERVISOR: all $T done"; break; fi
  echo "SUPERVISOR: relaunch at $n/$T $(date -u +%H:%M:%S)"
  python3 "$GEN" >> "$LOG" 2>&1
  sleep 5
done
