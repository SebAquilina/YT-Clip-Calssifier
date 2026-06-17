#!/usr/bin/env python3
"""I Inspected 50 Failed Candle Batches - The #1 Mistake Was Everywhere
FORMAT v5.3: same framework as POOR SCENT THROW v5.2 PLUS a HARD ban on any on-screen
text/captions/subtitles (Veo was rendering spoken lines as captions), strengthened
identity, and B-roll that explicitly forbids any human/face (only her hands)."""
import json, os
ROOT=os.path.dirname(os.path.abspath(__file__))
REF=open("/tmp/raw_ref.txt").read().strip()
RAW="https://raw.githubusercontent.com/SebAquilina/YT-Clip-Calssifier/claude/10-candle-hacks-video-xijwmv/video_ps_veo/assets"
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
# HARD no-text ban (the #1 fix this round) — repeated so Veo never renders captions/subtitles/UI
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

# ===== ACT 1 hook =====
th("I just spent a week inspecting fifty failed candle batches that real makers sent me, and I genuinely need to talk about what I found.")
th("Fifty batches. Sinkholes, wet spots, cracked tops, rough frosting, candles that barely smelled. Every kind of failure you can imagine was in that pile.")
th("And I went in fully expecting fifty different problems with fifty different causes. That is not what I found at all.")
th("Instead, one single mistake showed up in almost every single batch. It was absolutely everywhere.")
br("Fifty failed candles lined up on the bench, each one flawed in a different way.","slowly turns several flawed finished candles under the light, showing sinkholes, wet spots and rough tops")
th("And the scary part is, almost nobody who sent these in even knew they were making it. They were chasing the symptoms.")
th("They were buying new wax, new fragrance, new wicks, new jars, trying to fix four different problems, when it was really only ever one.")
th("So today I am going to show you the number one mistake, exactly how it causes all these different-looking defects, and how to fix it for good.")
th("Stick with me to the end, because the fix costs about ten dollars and takes thirty extra seconds per batch.")
th("Let me quickly tell you how I did this, because it matters. I burned, weighed, and cut open candles from every single batch.")
th("I logged the wax type, the fragrance load, the jar, the wick, and how each one was poured and cooled. Fifty little case files.")
th("And when I lined up the data, the pattern was almost embarrassing. The same column kept lighting up over and over.")
# ===== ACT 2 the reveal =====
th("So let me just tell you what it is, because it is going to sound almost too simple. It is temperature.")
th("Specifically, guessing the temperature instead of measuring it. Pouring too hot, adding fragrance at the wrong heat, and letting candles cool however they please.")
th("Out of fifty failed batches, forty-three of them traced straight back to temperature. Forty-three out of fifty.")
br("A kitchen thermometer sitting unused on the bench beside a pot of melted wax.","picks up a kitchen thermometer and lowers it into a pot of melted wax, watching the reading climb")
th("Almost everyone was pouring by feel, or by a timer, or just whenever the wax looked about ready. Almost nobody was actually measuring it.")
th("And wax does not care what it looks like. The temperature is doing chemistry whether you measure it or not.")
th("Every wax has a melt point, a fragrance-add temperature, and a pour temperature, and they are all different numbers.")
th("When you guess, you might be forty degrees off and have no idea. And forty degrees is the difference between a perfect candle and a ruined one.")
th("The reason this mistake is so sneaky is that temperature is invisible. A bad recipe you can see. The wrong heat looks exactly like the right heat.")
th("So you only find out you got it wrong hours later, when the candle has already set into whatever defect you accidentally baked into it.")
th("Let me show you exactly how this one invisible mistake turns into four completely different-looking failures.")
# ===== ACT 3 defect 1: wet spots / adhesion =====
th("Failure number one, and the most common by far. Wet spots. Those ugly patches where the wax pulls away from the glass.")
th("A huge number of people think wet spots are a moisture problem. They are not. They are a temperature problem.")
th("When you pour wax that is too hot into a cool jar, the wax expands against the glass, then shrinks hard as it cools and rips away from it.")
br("A finished jar candle held to the light showing cloudy patches where the wax has pulled off the glass.","tilts a glass jar candle toward the window, revealing cloudy wet-spot patches against the glass")
th("Those patches are just little pockets of air where the wax let go of the glass. And once they appear, you cannot fix them. The batch is cosmetically done.")
th("The fix is almost stupidly simple. Warm your jars before you pour, and pour in the right temperature window for your wax.")
th("Pre-warm the glass to roughly the same temperature as your pour, and the wax hugs the glass as it cools instead of recoiling from it.")
th("Eight of the fifty batches had wet spots, and every single one of them had been poured screaming hot into a cold jar straight off a shelf.")
# ===== ACT 4 defect 2: sinkholes =====
th("Failure number two. Sinkholes. You pour a beautiful candle, it sets, and the next morning there is a crater around the wick.")
th("A sinkhole is just the wax cooling unevenly. The top skins over while the middle is still liquid, and as that trapped middle cools it collapses inward.")
br("A cooled candle with a deep sinkhole crater collapsed around the wick.","points at a set candle with a deep sinkhole crater around the wick, tracing the dip with a finger")
th("Pouring too hot makes this dramatically worse, because there is more heat to lose and far more shrinkage on the way down.")
th("People see the crater and assume they did not pour enough wax. Usually they poured plenty, they just poured it way too hot.")
th("Pour in the correct window, cool your candles slowly and evenly, and most sinkholes simply never form in the first place.")
th("And for the stubborn ones, a gentle heat-gun pass over the top, or a small second pour once it has set, fixes it completely.")
th("Nine of the fifty had sinkholes, and almost all of them had also been poured far too hot. It is the same root cause as the wet spots.")
# ===== ACT 5 defect 3: frosting & rough tops =====
th("Failure number three. Frosting and rough, bumpy tops. That white crystal haze, and tops that look like cottage cheese.")
th("Soy wax is a natural product, and it genuinely wants to form crystals. Cooling it too fast in a cold room makes those crystals go completely wild.")
br("A close look at a candle top showing white frosting and a rough, uneven surface.","runs a fingertip lightly across a rough, frosted candle top, showing the bumpy uneven surface")
th("Pour too hot into a cold space and you get a thermal shock that wrecks the surface as it sets. The wax basically panics.")
th("Frosting is not a defect in the wax. It is the wax reacting to being treated roughly on the way down.")
th("Pour in the right window, into pre-warmed jars, in a draft-free room, and let them cool slowly, and the tops come out smooth and creamy.")
th("Twelve of the fifty batches were just thermal shock. Hot wax meeting a cold jar in a cold room. Nothing else was wrong with them.")
# ===== ACT 6 defect 4: fragrance / hot spots =====
th("Failure number four. Candles that barely smell, even with plenty of fragrance oil already in them.")
th("Now I did a whole separate video on scent throw, but a huge piece of it is temperature too, so it absolutely belongs in this list.")
th("Add your fragrance when the wax is too hot, and a big part of it just flashes off into the air before it can ever bind to the wax.")
br("Fragrance oil being poured into a pot of melted wax while a thermometer reads the temperature.","slowly pours fragrance oil from an amber bottle into the melted wax with a thermometer resting in the pot")
th("Add it when the wax is too cool, and it never fully blends in, so it sits there in little pockets doing almost nothing.")
th("You paid full price for that fragrance oil. Adding it at the wrong temperature is just pouring money straight into the air.")
th("Measure the wax, add your fragrance in the correct window, and stir gently for a full two minutes. The exact same oil suddenly works.")
th("I tested this on two batches from the same maker, same oil, same load. One added hot, one added in the window. The difference in throw was night and day.")
th("So before you ever blame your fragrance supplier, check the temperature you added it at. Nine times out of ten, that is the real culprit.")
# ===== ACT 7 the cooling environment =====
th("Now here is the part almost everyone forgets completely. Cooling is part of temperature too.")
th("You can pour at the perfect temperature and still ruin the candle in the next ten minutes if the cooling environment is wrong.")
br("A freshly poured candle cooling undisturbed on a shelf away from any window or draft.","sets a freshly poured candle on a clear shelf away from the window, leaving it undisturbed to cool")
th("Cold countertops, open windows, a draft from a fan, or shoving them in the fridge to rush it. All of that causes the exact defects we just covered.")
th("I had several batches where the pour was perfect, and the maker put them straight in front of a cold window to set faster. Every one frosted.")
th("Pour them, then leave them completely alone on a level surface, away from drafts, and let them come down to room temperature slowly.")
th("Do not move them, do not chase them with a fan, and never, ever put them in the fridge. Patience in that first hour saves the whole batch.")
th("Think of it like baking. You would not yank a cake out of the oven and stick it in the freezer to set faster. Wax is no different.")
th("A consistent, calm, room-temperature space is honestly worth more than any fancy wax or expensive fragrance you can buy.")
# ===== ACT 8 the method =====
th("So here is the simple system that would have saved almost all fifty of these batches.")
th("Number one. Buy a cheap kitchen thermometer and actually use it. Stop guessing, start measuring, every single pour.")
th("Number two. Add your fragrance and pour within the temperature window your specific wax recommends. It is printed right on the spec sheet.")
th("Number three. Pre-warm your jars so the hot wax is not shocked the instant it hits cold glass.")
th("Number four. Let everything cool slowly and undisturbed in a draft-free room. No fridge, no fan, no moving them around.")
br("The simple toolkit: a thermometer, clean pre-warmed jars and a calm draft-free space.","lays out a thermometer and a row of clean empty jars on the bench, ready for a careful measured pour")
th("That is it. Four boring, unglamorous steps, and they fix the one mistake that was quietly hiding inside almost every failure I inspected.")
th("No new wax, no new fragrance, no fancy equipment. Just a thermometer and a little patience.")
# ===== ACT 9 verdict + CTA =====
th("So here is the bottom line from fifty failed batches. It is almost never fifty different problems.")
th("It is usually one quiet mistake, guessing the temperature, just wearing four different costumes.")
th("Measure your wax, respect the cooling, and the wet spots, the sinkholes, the frosting and the weak scent mostly just disappear together.")
th("It is honestly the highest-value thirty seconds you can add to your whole process, and it costs about ten dollars.")
th("If this helped you finally make sense of your own failed batches, subscribe, because I break down one real candle problem like this every single week.")
th("And tell me down in the comments which of these four failures you have been fighting with. I read every one, and I will help where I can.")

# ---- build beats + gaps ----
def est(t): return max(1.5, round(len(t.split())/WPS+0.4,2))
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
print(f"50 FAILED BATCHES | {len(beats)} beats ({nth} TH + {nbr} B-roll) | {len(chains)} chains | est {total/60:.1f} min | TH ratio {th_t/total:.2f} | gaps {len(gaps)}")
folder=os.path.join(ROOT,"..","video_fail_veo")
os.makedirs(os.path.join(folder,"Project files"),exist_ok=True); os.makedirs(os.path.join(folder,"Source clips"),exist_ok=True)
M={"title":"I Inspected 50 Failed Candle Batches - The #1 Mistake Was Everywhere","channel":"Candice's Country Candles",
   "narrator_voice":VOICE,"aspect":"16:9","video_model":"veo-video","clip_len":8.0,"reference_photo_url":REF,
   "scenes":{k:v["anchor"] for k,v in SCENES.items()},"hands_ref_url":HANDS,"broll_refs":BROLL_REFS,"max_run":MAX_RUN,
   "continuity_bible":WS,"format":"th-dominant-chained-v5.3","chains":chains,"beats":beats,
   "gaps":{str(g):" ".join(b["sentence"] for b in beats if b.get("gap_id")==g) for g in gaps}}
json.dump(M,open(os.path.join(folder,"Project files","manifest.json"),"w"),indent=2)
print("wrote manifest.json")
