#!/usr/bin/env python3
"""master_audio.py <in.mp4> <out.mp4>
Final audio-mastering pass for a finished video:
  - high-pass 75 Hz (kill rumble) + light FFT denoise
  - two-pass EBU R128 loudnorm to -16 LUFS / -1.5 dBTP (uniform across the Veo
    talking-head audio and the TTS gap VO)
  - a very faint pink-noise room-tone bed (~-50 dB) so silence-trimmed seams are
    not jarring digital silence
Video stream is copied untouched."""
import sys, os, json, subprocess, re
FF="/usr/local/bin/ffmpeg"; FP="/usr/local/bin/ffprobe"
IN, OUT = sys.argv[1], sys.argv[2]
def dur(p):
    o=subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip()
    return float(o or 0)
def measure_lufs(p):
    r=subprocess.run([FF,"-i",p,"-af","loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json","-f","null","-"],capture_output=True,text=True)
    m=re.search(r"\{[^{}]*input_i[^{}]*\}",r.stderr,re.S)
    return json.loads(m.group(0)) if m else None
D=dur(IN)
print("pass1: measuring loudness...")
st=measure_lufs(IN)
if st:
    ln=(f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={st['input_i']}:measured_TP={st['input_tp']}:"
        f"measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true")
else:
    ln="loudnorm=I=-16:TP=-1.5:LRA=11"
print("pass2: mastering + room tone...")
fc=(f"[0:a]highpass=f=75,afftdn=nf=-28,{ln}[v0];"
    f"anoisesrc=color=pink:amplitude=0.0035:d={D+1:.1f}[bed];"
    f"[bed]highpass=f=120,lowpass=f=6000,volume=0.5[bedf];"
    f"[v0][bedf]amix=inputs=2:duration=first:weights=1 0.06:normalize=0[a]")
ok=subprocess.run([FF,"-y","-i",IN,"-filter_complex",fc,"-map","0:v:0","-map","[a]",
    "-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000","-ac","2","-movflags","+faststart",OUT],
    capture_output=True,text=True)
if ok.returncode!=0: print("ERR",ok.stderr[-400:]); sys.exit(1)
after=measure_lufs(OUT)
print(f"DONE: {OUT}")
if st: print(f"  input loudness  I={st['input_i']} LUFS  TP={st['input_tp']} dB")
if after: print(f"  output loudness I={after['input_i']} LUFS  TP={after['input_tp']} dB")
