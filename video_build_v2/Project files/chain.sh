#!/bin/bash
cd "/home/user/YT-Clip-Calssifier/video_build_v2/Project files"
export LABS69_API_KEY="vk_kokHYuBcZneKXXNZGaMzf3caxONeY3Wr"
echo "[chain] waiting for primary pass..." >> gen.log
while pgrep -f "python3 generate.py" >/dev/null; do sleep 10; done
echo "[chain] primary done -> enrichment build" >> gen.log
python3 build_100b.py >> gen.log 2>&1
echo "[chain] enrichment generate (re-TTS long + k1 angles)" >> gen.log
python3 generate.py >> gen.log 2>&1
echo "[chain] ENRICH COMPLETE" >> gen.log
