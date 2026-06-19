#!/usr/bin/env python3
"""polish.py <in.mp4> <out.mp4> <cta_start_sec> <cta_dur_sec>
Final polish pass applied to a delivered video:
  1) DELOGO the veo watermark in the bottom-right (the API's native removal is
     inconsistent, so we guarantee removal ourselves). Box tuned to the 1280x720
     'Veo' mark at x1225-1268,y692-708.
  2) During the CTA window, overlay the REAL high-res book cover as a clean inset
     (bottom-left) so viewers see the crisp title — veo only ever re-renders the
     book at low fidelity, so the real image is composited in.
Video re-encoded (crf 18, near-lossless); audio copied untouched."""
import sys, subprocess, os
FF="/usr/local/bin/ffmpeg"
IN,OUT=sys.argv[1],sys.argv[2]
cta=float(sys.argv[3]); dur=float(sys.argv[4]); end=cta+dur
BOOK="/home/user/YT-Clip-Calssifier/assets/book_cover.jpg"
# book inset: ~300px tall, bottom-left, subtle white border, only during CTA
fc=(
 "[1:v]scale=-1:300,pad=iw+8:ih+8:4:4:white[bk];"          # white border
 "[0:v]delogo=x=1198:y=676:w=78:h=40[dl];"                 # remove veo watermark
 f"[dl][bk]overlay=36:H-h-40:enable='between(t,{cta:.2f},{end:.2f})'[v]"
)
ok=subprocess.run([FF,"-y","-i",IN,"-i",BOOK,"-filter_complex",fc,"-map","[v]","-map","0:a",
  "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-c:a","copy",
  "-movflags","+faststart",OUT],capture_output=True,text=True)
if ok.returncode!=0: print("ERR",ok.stderr[-400:]); sys.exit(1)
print("POLISHED:",OUT)
