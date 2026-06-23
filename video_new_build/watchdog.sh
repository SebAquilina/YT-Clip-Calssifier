#!/usr/bin/env bash
# Self-healing watchdog: one pass. Relaunch any dead piece of the pipeline, then
# print a one-line status (used as the heartbeat event). Safe to run repeatedly.
export LABS69_API_KEY=vk_kokHYuBcZneKXXNZGaMzf3caxONeY3Wr
ROOT=/home/user/YT-Clip-Calssifier
RUN="$ROOT/video_ps_build/run_until_done.sh"
cd "$ROOT"

prog() { # $1 project dir -> "n/tot"
  python3 - "$1" <<'PY'
import json,sys,os
proj=sys.argv[1]
try:
    m=json.load(open(os.path.join(proj,"Project files","manifest.json"))); tot=len(m["beats"]); mids=set(b["id"] for b in m["beats"])
except Exception: print("0/0"); raise SystemExit
try:
    s=json.load(open(os.path.join(proj,"Project files","state.json")))
    n=sum(1 for i in mids if s["beats"].get(i,{}).get("job",{}).get("status")=="downloaded")
except Exception: n=0
print(f"{n}/{tot}")
PY
}
done_p() { local d; d=$(prog "$1"); [ "${d%/*}" = "${d#*/}" ] && [ "${d#*/}" != "0" ]; }

# Which project should be generating now? The first not-yet-complete one in order.
ACTIVE=""
for proj in video_fail_veo video_wicks_veo video_2v20_veo video_firstkit_veo; do
  if ! done_p "$ROOT/$proj"; then ACTIVE="$proj"; break; fi
done

HEAL=""
if [ -n "$ACTIVE" ]; then
  # ensure a generator is running; if not, ensure a supervisor is (it will spawn one)
  if ! pgrep -f "python3 .*generate_chained.py" >/dev/null; then
    if ! pgrep -f "run_until_done.sh .*$ACTIVE" >/dev/null; then
      nohup bash "$RUN" "$ROOT/$ACTIVE" "/tmp/${ACTIVE}_gen.log" >>/tmp/${ACTIVE}_sup.log 2>&1 &
      HEAL="$HEAL relaunched-sup($ACTIVE)"
    fi
  fi
fi
# keep the conductor alive (it sequences wicks->2v20->firstkit after fail)
if ! pgrep -f "conductor.sh" >/dev/null && [ "$ACTIVE" != "video_fail_veo" ]; then
  : # once past fail, the conductor's own loop handles the active project; supervisor above covers it
fi
if ! pgrep -f "conductor.sh" >/dev/null && ! done_p "$ROOT/video_firstkit_veo"; then
  nohup bash "$ROOT/video_new_build/conductor.sh" >>/tmp/conductor.log 2>&1 &
  HEAL="$HEAL relaunched-conductor"
fi

gen=$(pgrep -f "python3 .*generate_chained" >/dev/null && echo gen-up || echo GEN-DOWN)
con=$(pgrep -f "conductor.sh" >/dev/null && echo cond-up || echo cond-off)
echo "HEARTBEAT $(date -u +%H:%M) | fail:$(prog $ROOT/video_fail_veo) wicks:$(prog $ROOT/video_wicks_veo) 2v20:$(prog $ROOT/video_2v20_veo) firstkit:$(prog $ROOT/video_firstkit_veo) | active:$ACTIVE $gen $con${HEAL:+ | HEAL:$HEAL}"
