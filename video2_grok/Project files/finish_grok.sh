#!/bin/bash
cd "/home/user/YT-Clip-Calssifier/video2_grok/Project files"
while pgrep -f 'python3 generate.py' >/dev/null; do sleep 10; done
echo "[finish] grok gen done -> assembling" >> finish.log
python3 assemble.py >> asm.log 2>&1
echo "[finish] GROK ASSEMBLED" >> finish.log
