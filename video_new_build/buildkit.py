#!/usr/bin/env python3
"""buildkit.py — shared FORMAT v5.3 manifest builder for Candice videos.

Identical identity-lock / no-text / hands-only-B-roll / <=3-clip-chain / scene-rotation
rules as POOR SCENT THROW v5.2 and the 50-Failed-Batches v5.3 build. New videos only
supply a script (an ordered list of th()/br() beats) + title + output folder; everything
about prompting, chaining and the manifest shape is fixed here so identity and the
no-caption ban can never regress between videos.

Usage from a content module:
    from buildkit import th, br, build
    th("spoken talking-head line ...")
    br("on-screen description", "what HER hands do, hands only, no face")
    ...
    build(title="...", folder_name="video_xxx_veo")
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REF = open("/tmp/raw_ref.txt").read().strip()
RAW = "https://raw.githubusercontent.com/SebAquilina/YT-Clip-Calssifier/claude/10-candle-hacks-video-xijwmv/video_ps_veo/assets"
BENCH=f"{RAW}/bench_anchor.png"; KITCHEN=f"{RAW}/kitchen_anchor.png"; SHELF=f"{RAW}/shelf_anchor.png"
PACKING=f"{RAW}/packing_anchor.png"; WINDOW=f"{RAW}/window_anchor.png"
HANDS=f"{RAW}/hands_ref.png"; OVERHEAD=f"{RAW}/overhead_action.png"
BROLL_REFS=[HANDS,OVERHEAD]
SCENES={"bench":{"anchor":BENCH,"setting":"seated at her rustic wooden candle-workshop workbench"},
        "kitchen":{"anchor":KITCHEN,"setting":"standing at her kitchen stove station, a pot of melting wax beside her"},
        "shelf":{"anchor":SHELF,"setting":"standing beside her curing shelf of finished candles"},
        "packing":{"anchor":PACKING,"setting":"standing at her packing and labeling table with kraft boxes and finished candles"},
        "window":{"anchor":WINDOW,"setting":"seated by a bright window at a small side table with a notebook"}}
JUMP_SCENES=["kitchen","shelf","packing","window"]
MAX_RUN=3
VOICE={"provider":"minimax-clone","voiceCloneId":"6f906e1c-3bcd-404f-9f35-e16c76a98be1",
       "model":"speech-2.8-hd","speed":1.05,"language_boost":"en"}
WPS=3.2
WS=("an ordinary lived-in home candle workshop: a worktable with glass candle jars, bags of soy wax, "
"amber fragrance-oil bottles, a kitchen thermometer, a small scale, a stovetop pot and a curing shelf of "
"finished candles, natural daylight.")
NOTEXT=("ABSOLUTELY NO on-screen text of ANY kind: no subtitles, no captions, no transcription of her "
"speech, no words, no letters, no numbers, no title text, no lower-thirds, no REC indicator, no red dot, "
"no battery icon, no camera viewfinder or UI, no timecode, no watermark, no logos. The video frame contains "
"only the real photographed scene and nothing overlaid.")
IDENTITY=("This is the EXACT SAME woman shown in the reference keyframe image — identical face, identical "
"tortoiseshell glasses, identical curly grey hair, blue knit sweater and tan apron. She is white, in her "
"mid-fifties. Do NOT change her face, age, or ethnicity into a different person. ")
PHONE=("filmed as casual amateur smartphone footage: handheld, slight natural shake, natural available light, "
"slightly flat auto-exposure, deep focus, candid vlog feel. Photo-real and physically correct; nothing spawns "
"in or vanishes; hands have exactly five fingers; continuous subtle motion, never a frozen frame.")
TH_STRICT=("Exactly ONE person, a single solid subject — no second face, no double exposure, no ghosting, no "
"morphing, no extra hands; natural blink and lip-sync; steady framing; natural window light. The first frame "
"is already this exact woman, sharp and in focus, no fade-in or morph. She is already mid-conversation: begins "
"the first word immediately with no inhale, speaks continuously without freezing, no big inhale at the end.")
LABELS=("Background candle jars may carry small, tidy, real printed product labels (short words like "
"\"Lavender\", \"Soy Wax\"); these are physical labels on the jars, NOT on-screen text.")

def th_continue(line):
    return (f"{IDENTITY}The exact same woman in the same candle workshop continues speaking directly to the camera "
    f"in a warm American accent, lips fully in sync, saying exactly: \"{line}\". {TH_STRICT} {LABELS} {NOTEXT} "
    f"Casual handheld smartphone vlog look. Setting: {WS}")
def th_scene(line,scene,moved):
    s=SCENES[scene]["setting"]
    move=(f"She has just moved and is now {s}, settling naturally into frame with gentle continuous movement as she "
          f"keeps talking. " if moved else f"She is {s}, looking straight at camera. ")
    return (f"{IDENTITY}{move}She speaks directly to the camera in a warm American accent, lips fully in sync, saying "
    f"exactly: \"{line}\". {TH_STRICT} {LABELS} {NOTEXT} Casual handheld smartphone vlog look. Setting: {WS}")
def hands_prompt(subj):
    return (f"Close-up point-of-view of ONLY the hands and forearms of the same woman (matching the reference hands "
    f"image: mid-fifties, fair naturally-aged skin, plain wedding band, blue sweater cuffs and tan apron) as she "
    f"{subj}, on her own candle-workshop bench. Her hands ONLY — absolutely NO face, NO head, NO other person or "
    f"human anywhere in frame. {PHONE} {NOTEXT} Setting: {WS}")

B=[]
def th(t): B.append(("th",t,None))
def br(t,subj): B.append(("broll",t,subj))

def est(t): return max(1.5, round(len(t.split())/WPS+0.4,2))

def build(title, folder_name, channel="Candice's Country Candles"):
    beats=[]; gap=0; prev=None; br_n=0
    for i,(typ,text,subj) in enumerate(B):
        if typ=="broll":
            if prev!="broll": gap+=1
            beats.append({"id":f"b{i:02d}_g{gap}","type":"broll","sentence":text,"visual_subject":subj,
                          "gap_id":gap,"prompt":hands_prompt(subj),"broll_ref":BROLL_REFS[br_n%len(BROLL_REFS)],"dur":est(text)})
            br_n+=1
        else:
            beats.append({"id":f"b{i:02d}_th","type":"character","sentence":text,"dur":est(text)})
        prev=typ
    chains=[]; i=0; jump_idx=0; cid=0
    while i<len(beats):
        if beats[i]["type"]!="character": i+=1; continue
        run=[]; j=i
        while j<len(beats) and beats[j]["type"]=="character": run.append(beats[j]); j+=1
        for k in range(0,len(run),MAX_RUN):
            sub=run[k:k+MAX_RUN]; is_jump=(k>0)
            scene=JUMP_SCENES[jump_idx%len(JUMP_SCENES)] if is_jump else "bench"
            if is_jump: jump_idx+=1
            seed=SCENES[scene]["anchor"]
            for pos,b in enumerate(sub):
                b["prompt"]=th_scene(b["sentence"],scene,moved=is_jump) if pos==0 else th_continue(b["sentence"])
            chains.append({"id":cid,"scene":scene,"seed_keyframe_url":seed,"beat_ids":[b["id"] for b in sub]}); cid+=1
        i=j
    total=sum(b["dur"] for b in beats); th_t=sum(b["dur"] for b in beats if b["type"]=="character")
    gaps=sorted(set(b["gap_id"] for b in beats if b["type"]=="broll"))
    nth=sum(1 for b in beats if b["type"]=="character"); nbr=len(beats)-nth
    print(f"{title[:40]} | {len(beats)} beats ({nth} TH + {nbr} B-roll) | {len(chains)} chains | est {total/60:.1f} min | TH ratio {th_t/total:.2f} | gaps {len(gaps)}")
    folder=os.path.join(ROOT,"..",folder_name)
    os.makedirs(os.path.join(folder,"Project files"),exist_ok=True); os.makedirs(os.path.join(folder,"Source clips"),exist_ok=True)
    M={"title":title,"channel":channel,
       "narrator_voice":VOICE,"aspect":"16:9","video_model":"veo-video","clip_len":8.0,"reference_photo_url":REF,
       "scenes":{k:v["anchor"] for k,v in SCENES.items()},"hands_ref_url":HANDS,"broll_refs":BROLL_REFS,"max_run":MAX_RUN,
       "continuity_bible":WS,"format":"th-dominant-chained-v5.3","chains":chains,"beats":beats,
       "gaps":{str(g):" ".join(b["sentence"] for b in beats if b.get("gap_id")==g) for g in gaps}}
    json.dump(M,open(os.path.join(folder,"Project files","manifest.json"),"w"),indent=2)
    print("wrote",os.path.join(folder,"Project files","manifest.json"))
    return M
