#!/usr/bin/env python3
"""gen_dt_par.py <project_dir> [--vid 5] [--img 7] [--tts 5] — CONCURRENT generator.

Saturates the API limits: up to 5 concurrent veo videos, 7 concurrent nano-banana images, and
parallel TTS, all in ONE process. Beats are independent, so they run concurrently; resource
semaphores cap each API type at its limit. A single state.json is written under a lock (no
cross-process race). Resumable: already-finished assets are skipped.

Generation ORDER does not affect the final video — the assembler reads beats in manifest order,
so concurrency is purely a speed-up; flow/continuity is unchanged.
"""
import sys, os, json, threading, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import imgkit as K
def argf(flag,d): return int(sys.argv[sys.argv.index(flag)+1]) if flag in sys.argv else d
PROJ=sys.argv[1]; PF=os.path.join(PROJ,"Project files")
SRC=os.path.join(PROJ,"Source clips"); IMG=os.path.join(PROJ,"images"); AUD=os.path.join(PF,"audio")
for d in (SRC,IMG,AUD): os.makedirs(d,exist_ok=True)
M=json.load(open(os.path.join(PF,"manifest.json")))
SP=os.path.join(PF,"state.json")
S=json.load(open(SP)) if os.path.exists(SP) else {"beats":{}}
VID=argf("--vid",5); IMGN=argf("--img",7); TTSN=argf("--tts",2)  # TTS limit is 2 concurrent
vid_sem=threading.Semaphore(VID); img_sem=threading.Semaphore(IMGN); tts_sem=threading.Semaphore(TTSN)
lock=threading.Lock()
def save():
    with lock: json.dump(S,open(SP,"w"),indent=2)
def st(bid):
    with lock: return S["beats"].setdefault(bid,{})
def have(p): return bool(p and os.path.exists(p) and os.path.getsize(p)>2000)
def vid_ok(p): return have(p) and K.dur(p)>0.4
def setk(bid,k,v):
    # update + flush atomically under the lock (json.dump must not run while another thread mutates S)
    with lock:
        S["beats"].setdefault(bid,{})[k]=v
        json.dump(S,open(SP,"w"),indent=2)

def gen_image_sem(prompt,dest,refs,ar):
    with img_sem: return K.gen_image(prompt,dest,image_urls=refs,aspect=ar)
def gen_video_sem(prompt,dest,urls,mode,muted):
    with vid_sem: return K.gen_video(prompt,dest,image_urls=urls,mode=mode,muted=muted)
def tts_sem_call(text,dest):
    with tts_sem: return K.tts(text,dest)

def host_img(path):
    # host a local image and return a public URL (used to chain a canonical subject into other shots)
    for _ in range(5):
        r=subprocess.run(["curl","-s","-m","90","-F","reqtype=fileupload","-F","time=72h","-F",
            f"fileToUpload=@{path}","https://litterbox.catbox.moe/resources/internals/api.php"],capture_output=True,text=True)
        if r.stdout.strip().startswith("http"): return r.stdout.strip()
    return None
def host_beat_image(refid):
    # host (and cache) the rendered image of an earlier beat so a later beat can reuse it as a reference
    with lock:
        u=S.get("subjects_bybeat",{}).get(refid)
        if u: return u
        rp=S["beats"].get(refid,{}).get("image")
    if not have(rp): return None   # ref not rendered yet -> caller should defer
    u=host_img(rp)
    if u:
        with lock: S.setdefault("subjects_bybeat",{})[refid]=u; json.dump(S,open(SP,"w"),indent=2)
    return u
def subject_ref(b):
    # v6.3/v6.4: feed a prior render in as the FIRST img2img reference so the subject stays consistent.
    # (a) explicit subject_key -> the hosted canonical; (b) auto subject_ref_of -> the linked earlier beat.
    # Returns: (url) ready, "WAIT" if the linked beat isn't rendered yet, or None if no chain.
    key=b.get("subject_key")
    if key:
        with lock: u=S.get("subjects",{}).get(key)
        return u
    refid=b.get("subject_ref_of")
    if refid:
        return host_beat_image(refid) or "WAIT"
    return None

def do_beat(b):
    bid=b["id"]; vm=b.get("visual_mode",b.get("type")); e=st(bid)
    tag=f"[{bid}/{vm}]"
    # 1) still image (full/split/live) — image pool
    if vm in ("image_full","image_split","image_live") and not have(e.get("image")):
        img=os.path.join(IMG,f"{bid}.png")
        sref=subject_ref(b)
        if sref=="WAIT":   # auto-chained to an earlier beat that isn't rendered yet — defer to next pass
            print(tag,"defer (waiting on subject ref",b.get("subject_ref_of"),")",flush=True); return
        base=[b["image_ref_url"]] if b.get("image_ref_url") else ([K.BENCH_REF] if K.BENCH_REF else [])
        refs=([sref]+base) if sref else (base or None)
        ar=b.get("ar","16:9")
        if gen_image_sem(b["image_prompt"],img,refs,ar):
            setk(bid,"image",os.path.abspath(img)); print(tag,"image ok",flush=True)
            # if this beat is the canonical for its subject, host it so later beats can reference it
            key=b.get("subject_key")
            if key and bid==CANON.get(key) and not subject_ref(b):
                u=host_img(img)
                if u:
                    with lock: S.setdefault("subjects",{})[key]=u; json.dump(S,open(SP,"w"),indent=2)
                    print(tag,f"hosted canonical subject '{key}'",flush=True)
        else: print(tag,"image FAIL",flush=True)
    # 2) TH clip (talking_head/image_split) — video pool
    if vm in ("talking_head","image_split") and not vid_ok(e.get("clip")):
        clip=os.path.join(SRC,f"{bid}.mp4")
        if gen_video_sem(b["prompt"],clip,[b["seed"]],"keyframes",False):
            setk(bid,"clip",os.path.abspath(clip)); print(tag,"TH clip ok",flush=True)
        else: print(tag,"TH clip FAIL",flush=True)
    # 3) come-to-life (live): host the still then animate — video pool (after image)
    if vm=="image_live" and not vid_ok(e.get("clip")) and have(e.get("image")):
        clip=os.path.join(SRC,f"{bid}.mp4"); url=None
        for _ in range(5):
            r=subprocess.run(["curl","-s","-m","90","-F","reqtype=fileupload","-F","time=72h","-F",
                f"fileToUpload=@{e['image']}","https://litterbox.catbox.moe/resources/internals/api.php"],capture_output=True,text=True)
            if r.stdout.strip().startswith("http"): url=r.stdout.strip(); break
        if url and gen_video_sem(K.live_motion(b["motion"]),clip,[url],"keyframes",True):
            setk(bid,"clip",os.path.abspath(clip)); print(tag,"live clip ok",flush=True)
        else: print(tag,"live clip FAIL",flush=True)
    # 4) broll hands (muted) — video pool
    if vm=="broll" and not vid_ok(e.get("clip")):
        clip=os.path.join(SRC,f"{bid}.mp4")
        if gen_video_sem(b["prompt"],clip,[b.get("broll_ref",K.HANDS)],"keyframes",True):
            setk(bid,"clip",os.path.abspath(clip)); print(tag,"broll clip ok",flush=True)
        else: print(tag,"broll clip FAIL",flush=True)
    # 5) TTS narration (full/live/broll) — tts pool (skippable via --notts so a dedicated TTS filler can own it)
    if "--notts" not in sys.argv and vm in ("image_full","image_live","broll") and b.get("narration") and not have(e.get("audio")):
        mp3=os.path.join(AUD,f"{bid}.mp3")
        for _ in range(3):
            if tts_sem_call(b["narration"],mp3):
                setk(bid,"audio",os.path.abspath(mp3)); setk(bid,"adur",K.dur(mp3)); print(tag,"tts ok",flush=True); break
        else: print(tag,"tts FAIL",flush=True)

def beat_done(b):
    vm=b.get("visual_mode",b.get("type")); e=S["beats"].get(b["id"],{})
    return ((vm=="talking_head" and vid_ok(e.get("clip"))) or
            (vm=="image_split" and vid_ok(e.get("clip")) and have(e.get("image"))) or
            (vm=="image_full" and have(e.get("image")) and have(e.get("audio"))) or
            (vm=="image_live" and vid_ok(e.get("clip")) and have(e.get("audio"))) or
            (vm=="broll" and vid_ok(e.get("clip")) and have(e.get("audio"))))

# v6.3 subject-reference: canonical = first beat (manifest order) with each subject_key.
CANON={}
for b in M["beats"]:
    k=b.get("subject_key")
    if k and k not in CANON: CANON[k]=b["id"]
# v6.4: chain ROOTS = beats referenced by an auto subject_ref_of that don't themselves reference anything.
# Pre-render heads (subject_key canonicals + chain roots) so the rest can chain off existing images.
_refed=set(b.get("subject_ref_of") for b in M["beats"] if b.get("subject_ref_of"))
def _is_root(b): return b["id"] in _refed and not b.get("subject_ref_of") and not b.get("subject_key")
head_ids=set(CANON.values()) | set(b["id"] for b in M["beats"] if _is_root(b))
head_beats=[b for b in M["beats"] if b["id"] in head_ids and not have(S["beats"].get(b["id"],{}).get("image"))]
if head_beats:
    print(f"subject pre-pass: {len(head_beats)} chain-head image(s): {[b['id'] for b in head_beats]}",flush=True)
    with ThreadPoolExecutor(max_workers=IMGN) as ex:
        for f in as_completed([ex.submit(do_beat,b) for b in head_beats]):
            try: f.result()
            except Exception as ex2: print("head error:",ex2,flush=True)

todo=[b for b in M["beats"] if not beat_done(b)]
print(f"concurrent gen: {len(todo)}/{len(M['beats'])} beats to do | vid={VID} img={IMGN} tts={TTSN}",flush=True)
with ThreadPoolExecutor(max_workers=VID+IMGN+TTSN+6) as ex:
    futs=[ex.submit(do_beat,b) for b in todo]
    for f in as_completed(futs):
        try: f.result()
        except Exception as ex2: print("beat error:",ex2,flush=True)
save()
done=sum(1 for b in M["beats"] if beat_done(b))
print(f"GEN DONE: {done}/{len(M['beats'])} beats complete",flush=True)
