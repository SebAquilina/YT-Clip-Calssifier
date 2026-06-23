#!/usr/bin/env python3
"""Regenerate all B-roll narration audio with the manifest's current voice."""
import json, os, time, urllib.request, urllib.error, subprocess
BASE="https://69labs.vip/api/v1"; KEY=os.environ["LABS69_API_KEY"]
ROOT=os.path.dirname(os.path.abspath(__file__)); AUD=os.path.join(ROOT,"audio")
FP="/usr/local/bin/ffprobe"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
M=json.load(open(os.path.join(ROOT,"manifest.json"))); V=M["narrator_voice"]
def req(method,path,body=None,t=60):
    url=BASE+path; data=json.dumps(body).encode() if body else None
    h={"Authorization":f"Bearer {KEY}","User-Agent":UA,"Accept":"application/json"}
    if data:h["Content-Type"]="application/json"
    r=urllib.request.Request(url,data=data,headers=h,method=method)
    for _ in range(5):
        try:
            with urllib.request.urlopen(r,timeout=t) as resp: return resp.status,json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(8); continue
            return e.code,{"error":e.read().decode()[:200]}
        except Exception: time.sleep(4)
    return 0,{"error":"x"}
def dur(p):
    o=subprocess.run([FP,"-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",p],capture_output=True,text=True).stdout.strip()
    try:return float(o)
    except:return 0
for b in M["beats"]:
    if b["type"]!="broll": continue
    dest=os.path.join(AUD,f"{b['id']}.mp3")
    st,j=req("POST","/tts/generate",{"text":b["sentence"],"voiceProvider":V["provider"],"voiceId":V["voiceId"],"modelId":V["modelId"]})
    jid=j.get("id")
    if not jid: print("FAIL create",b["id"],j); continue
    for _ in range(40):
        time.sleep(3); st,s=req("GET",f"/tts/status/{jid}")
        if s.get("status")=="COMPLETED": break
        if s.get("status") in("FAILED","CENSORED"): print("FAIL",b["id"],s.get("status")); jid=None; break
    if not jid: continue
    r=urllib.request.Request(f"{BASE}/tts/download/{jid}",headers={"Authorization":f"Bearer {KEY}","User-Agent":UA})
    with urllib.request.urlopen(r,timeout=120) as resp,open(dest,"wb") as f: f.write(resp.read())
    print(f"{b['id']} dur={dur(dest):.1f}s size={os.path.getsize(dest)}")
print("RETTS DONE")
