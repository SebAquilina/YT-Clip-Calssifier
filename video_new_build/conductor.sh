#!/usr/bin/env bash
# Sequential generation conductor. Waits for the fail video to finish generating,
# then runs the 3 new-video generators back-to-back (one at a time — the 69labs
# backend only allows 5 concurrent clips, so parallel generators would just collide).
# Each project is driven by run_until_done.sh (the resumable supervisor).
set -u
export LABS69_API_KEY=vk_kokHYuBcZneKXXNZGaMzf3caxONeY3Wr
ROOT=/home/user/YT-Clip-Calssifier
RUN="$ROOT/video_ps_build/run_until_done.sh"

downloaded() { # $1 = project dir -> echoes "n/total"
  python3 - "$1" <<'PY'
import json,sys,os
p=os.path.join(sys.argv[1],"Project files","manifest.json")
sp=os.path.join(sys.argv[1],"Project files","state.json")
try:
    m=json.load(open(p)); tot=len(m["beats"])
except Exception: print("0/0"); raise SystemExit
try:
    s=json.load(open(sp)); n=sum(1 for b in s.get("beats",{}).values() if b.get("job",{}).get("status")=="downloaded")
except Exception: n=0
print(f"{n}/{tot}")
PY
}
all_done() { local d; d=$(downloaded "$1"); [ "${d%/*}" = "${d#*/}" ] && [ "${d#*/}" != "0" ]; }

# 1) Wait for the fail video (already generating under its own supervisor) to complete.
echo "CONDUCTOR: waiting for fail video to finish generating..."
while ! all_done "$ROOT/video_fail_veo"; do
  echo "CONDUCTOR: fail $(downloaded "$ROOT/video_fail_veo")"
  sleep 120
done
echo "CONDUCTOR: fail video generation COMPLETE."

# 2) Generate the 3 new videos sequentially.
for proj in video_wicks_veo video_2v20_veo video_firstkit_veo; do
  D="$ROOT/$proj"
  if all_done "$D"; then echo "CONDUCTOR: $proj already complete, skipping"; continue; fi
  echo "CONDUCTOR: starting generation for $proj"
  # kill any stale generator first
  pkill -f "run_until_done.sh .*$proj" 2>/dev/null
  bash "$RUN" "$D" "/tmp/${proj}_gen.log" >/tmp/${proj}_sup.log 2>&1 &
  SUP=$!
  while ! all_done "$D"; do
    if ! kill -0 "$SUP" 2>/dev/null && ! pgrep -f "python3 .*generate_chained.py" >/dev/null; then
      echo "CONDUCTOR: $proj supervisor died at $(downloaded "$D"), relaunching"
      bash "$RUN" "$D" "/tmp/${proj}_gen.log" >>/tmp/${proj}_sup.log 2>&1 &
      SUP=$!
    fi
    echo "CONDUCTOR: $proj $(downloaded "$D")"
    sleep 120
  done
  echo "CONDUCTOR: $proj generation COMPLETE."
done
echo "CONDUCTOR: ALL GENERATION COMPLETE."
