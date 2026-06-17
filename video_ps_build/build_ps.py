#!/usr/bin/env python3
"""POOR SCENT THROW (v2 rules): talking-head-dominant, FORMAT v5.
NEW RULES:
- Max 3 talking-head clips per chain. Longer stretches are split.
- Chains seed from a SCENE ANCHOR. Default = workbench. A scene CHANGE
  (bench -> kitchen/stove -> curing shelf, rotating) happens ONLY on a direct
  talking-head -> talking-head jump-cut (i.e. a split inside a contiguous TH run,
  with no B-roll between). After B-roll she returns to the bench.
- The first clip of a jump-cut chain gets a "moved to <scene>, settling, mild
  movement" beat so the cut reads as an intentional location change.
- B-roll = HER hands in HER workspace (seeded from hands_ref), never generic.
- Labels/printed text ALLOWED on background jars in talking-head (static) shots;
  kept OFF moving B-roll (Veo garbles text in motion).
- Voice = MiniMax cloned voice "candice" via /voice-clones/generate, speed 1.05.
The generator (generate_chained.py) consumes manifest["chains"] directly:
each chain's first clip uses seed_keyframe_url; the rest chain off the EXACT last
frame of the previous clip."""
import json, os
ROOT=os.path.dirname(os.path.abspath(__file__))
REF=open("/tmp/raw_ref.txt").read().strip()
BENCH=open("/tmp/th_startframe_url.txt").read().strip()
RAW="https://raw.githubusercontent.com/SebAquilina/YT-Clip-Calssifier/claude/10-candle-hacks-video-xijwmv/video_ps_veo/assets"
KITCHEN=f"{RAW}/kitchen_anchor.png"; SHELF=f"{RAW}/shelf_anchor.png"; HANDS=f"{RAW}/hands_ref.png"
SCENES={"bench":{"anchor":BENCH,"setting":"at her rustic wooden candle-workshop workbench"},
        "kitchen":{"anchor":KITCHEN,"setting":"at her kitchen stove station, a pot of melting wax beside her"},
        "shelf":{"anchor":SHELF,"setting":"beside her curing shelf of finished candles"}}
JUMP_SCENES=["kitchen","shelf"]   # rotated on direct TH->TH jump-cuts
MAX_RUN=3
VOICE={"provider":"minimax-clone","voiceCloneId":"6f906e1c-3bcd-404f-9f35-e16c76a98be1",
       "model":"speech-2.8-hd","speed":1.05,"language_boost":"en"}
WPS=3.2  # measured rate of the candice clone at speed 1.05
WS=("an ordinary lived-in home candle workshop: a worktable with glass candle jars, bags of soy wax, "
"amber fragrance-oil bottles, a kitchen thermometer, a small scale, a stovetop pot and a curing shelf "
"of finished candles, natural daylight.")
PHONE=("filmed as casual amateur smartphone footage: handheld, slight natural shake, natural available "
"light, slightly flat auto-exposure, deep focus, candid vlog feel. No on-screen camera UI, REC dot, "
"battery icon, captions, watermark or logos. Photo-real and physically correct; nothing spawns in or "
"vanishes; hands have exactly five fingers; continuous subtle motion, never a frozen frame.")
TH_STRICT=("Exactly ONE person, a single solid subject — no second face, no double exposure, no ghosting, "
"no morphing, no extra hands; natural blink and lip-sync; steady framing; natural window light. The first "
"frame is already this exact woman, sharp and in focus, no fade-in or morph. She is already mid-conversation: "
"begins the first word immediately with no inhale or pause, speaks continuously without freezing, no big "
"inhale at the end. No on-screen camera UI, REC dot or battery icon.")
LABELS=("Background candle jars may show small, simple, tidy printed labels with short real words such as "
"\"Lavender\", \"Soy Wax\" or \"Vanilla\"; keep any text clean and legible, not garbled.")

def th_continue(line):
    return (f"The exact same woman in the same candle workshop continues speaking directly to the camera in a "
    f"warm American accent, lips fully in sync, saying exactly: \"{line}\". {TH_STRICT} {LABELS} Casual "
    f"handheld smartphone vlog look. Setting: {WS}")
def th_scene(line,scene,moved):
    s=SCENES[scene]["setting"]
    move=(f"She has just moved to a new spot and is now {s}, settling naturally into frame with gentle "
          f"continuous movement as she keeps talking. " if moved else f"She is {s}, looking straight at camera. ")
    return (f"The exact same woman as the reference, {move}speaking directly to the camera in a warm American "
    f"accent, lips fully in sync, saying exactly: \"{line}\". {TH_STRICT} {LABELS} Casual handheld smartphone "
    f"vlog look. Setting: {WS}")
def hands_prompt(subj):
    return (f"Close-up point-of-view of the SAME woman's hands and forearms (matching the reference hands image: "
    f"mid-fifties, fair naturally-aged skin, plain wedding band, blue sweater cuffs and tan apron) as she {subj}, "
    f"on her own candle-workshop bench. Her hands only, no face. {PHONE} No printed text or labels visible on this "
    f"moving shot. Setting: {WS}")

B=[]
def th(t): B.append(("th",t,None))
def br(t,subj): B.append(("broll",t,subj))

# ===== ACT 1 hook =====
th("If your candles have a weak scent throw, I already know exactly what you are about to do. You are about to add more fragrance oil.")
th("Please, stop right there. That is the single most common mistake I see, and nine times out of ten it makes the problem worse, not better.")
th("I have made candles for fifteen years, and I promise you the answer is almost never just more oil.")
th("By the end of this video you are going to understand the real reasons a candle does not throw, and how to actually fix every one of them.")
br("You light a beautiful candle, lean in close, and barely smell a thing.","leans over a freshly lit candle and gently fans the scent toward herself, looking a little disappointed")
th("It is one of the most frustrating things in this whole hobby. You did everything right, and the room still smells like nothing.")
# ===== ACT 2 the myth / max load =====
th("So before we fix anything, let me kill the myth at the center of all of this.")
th("Scent throw is not simply more oil equals more smell. That is just not how wax chemistry works.")
th("Every single wax has a maximum fragrance load. It is the most oil that wax can actually hold and bind to.")
th("For most soy waxes that ceiling is somewhere around eight to ten percent of the wax weight.")
br("Ten percent is the ceiling, and you measure it on a scale, not by eye.","sets a jar of wax on a small digital kitchen scale and holds an amber fragrance-oil bottle, reading the weight")
th("Your wax supplier publishes that number. It is on the spec sheet, and it is worth looking up before you pour anything.")
th("Now here is what happens when you ignore it and go past that ceiling.")
th("The wax physically cannot hold the extra oil. There is simply nowhere left for it to bind inside the wax.")
br("So it leaches back out and pools as oily sweat on top of the candle.","tilts a finished candle under the light, showing shiny oily beads of fragrance sweating on its surface")
th("That sweating oil does not make the candle smell stronger. It just sits there, wasted, on the surface.")
th("Worse than that, it looks unprofessional, it can ruin your label, and pooled oil near a flame is genuinely a fire risk.")
th("So more oil past the limit gives you a weaker, greasier, more dangerous candle, not a stronger one. Less is genuinely more here.")
# ===== ACT 3 cure time =====
th("Okay, so if it is not the oil, what is it? Let me give you the real issues, starting with the biggest one by far.")
th("Real issue number one is cure time. And honestly, if you only fix one thing from this whole video, make it this.")
th("Here is what most people never understand. The moment you pour, your fragrance is just floating in liquid wax.")
th("It has not bonded to anything yet. It is basically just oil suspended in a hot puddle.")
th("As that wax cools and hardens over the next several days, the oil slowly binds into the wax structure on a molecular level.")
th("That binding process is what actually lets the scent release steadily into the air when you burn it. That is the throw.")
br("That is why serious makers cure every candle on a shelf for a week or two before they ever sell it.","runs a hand along a shelf of curing candles and turns a small handwritten date tag beside one")
th("Soy candles need at least one to two weeks of curing to throw their absolute best. Some makers swear by a full month.")
th("But here is what almost everyone does instead. They pour the candle, and they burn it that very same day.")
th("They smell almost nothing, they decide the recipe is broken, and they go add more oil to the next batch.")
th("It is not a bad recipe. It is just an impatient one. Cure that exact same candle for two weeks and it transforms.")
th("I have had candles that smelled like nothing on day one become my best sellers by day fourteen. Same wax, same oil, just patience.")
# ===== ACT 4 binding temperature =====
th("Real issue number two is the temperature you add your fragrance at. This one is sneaky.")
th("If you add your oil to wax that is too cool, it never fully mixes in, and it never properly binds.")
th("But if you add it when the wax is too hot, a big chunk of your fragrance literally burns off into the air before it ever cools.")
th("Either way, you have just thrown away part of the scent you paid good money for.")
br("The sweet spot is right around 185 degrees, checked with a thermometer, not guessed.","holds a kitchen thermometer in a pot of melted wax reading about 185 degrees, then pours in fragrance oil")
th("For most soy wax, the sweet spot is right around 185 degrees Fahrenheit. Check your specific wax, but that is the ballpark.")
th("And please, use an actual thermometer. Guessing by eye is how you end up forty degrees off without ever knowing it.")
th("Once you hit that temperature, add your fragrance, and then stir gently and steadily for a full two minutes.")
br("Two full minutes of slow stirring is what actually locks the oil into the wax.","slowly and steadily stirs fragrance into a pitcher of melted wax with a spatula")
th("I know two minutes feels like forever when you are standing there stirring. Time it on your phone anyway.")
th("Rush that stir, and half your fragrance never properly bonds with the wax. It is the most skipped step in all of candle making.")
# ===== ACT 5 wick / melt pool =====
th("Real issue number three, and almost nobody talks about this one. Your wick.")
th("This sounds unrelated to scent, but it is one of the biggest factors of all. Let me explain why.")
th("When a candle burns, the scent does not come from the wax sitting there cold. It comes from the melt pool.")
th("The melt pool is that pool of hot liquid wax that forms around the flame. That is where the fragrance evaporates from.")
br("A wick that is too small makes a tiny flame and a tiny melt pool, so barely any scented wax is being warmed.","points at a candle burning with a small flame and only a narrow ring of melted wax, the rest still solid")
th("So if your wick is too small, you get a tiny flame, and only a thumbnail of wax ever melts.")
th("That means only that tiny bit of fragrance is being warmed and released into the room. The rest of your scent is locked in solid wax.")
th("You could have the best oil in the world at the perfect load, and a too-small wick will still strangle the throw.")
th("The fix is to size your wick to your jar, so the melt pool reaches the edges within a few hours of burning.")
br("A full, edge-to-edge melt pool releases far more scent than any amount of extra oil ever could.","gestures at a candle burning with a wide full melt pool of liquid wax right to the edges of the jar")
th("Honestly, going up just one wick size will usually do more for your throw than adding two percent more fragrance ever would.")
th("So before you touch the oil, ask yourself if your candle is even reaching a full melt pool.")
# ===== ACT 6 cold vs hot throw =====
th("Now there is one more thing I need you to get straight, because people judge candles wrong all the time.")
th("You need to know which kind of throw you are even measuring. There are two, and they are completely different.")
th("Cold throw is the scent you get when the candle is sitting there unlit. Hot throw is the scent when it is actively burning.")
br("Some oils smell incredible cold in the jar, and then go strangely quiet once they are lit.","lifts an unlit candle to her nose to smell it, then sets it down beside the same candle now lit and burning")
th("Some fragrance oils are amazing cold and disappointing hot. Others are the complete opposite. It depends on the oil.")
th("So do not throw out a recipe just because the cold throw is shy. Light it, let it reach a full pool, and then judge the hot throw.")
th("Judging a candle by sniffing the cold jar is like judging a meal by smelling the raw ingredients. You have to actually cook it.")
# ===== ACT 7 other truths =====
th("Alright, a few more quick truths, and every one of these matters more than dumping in extra oil.")
th("First, cheap fragrance oil is very often just weak fragrance oil. You are paying for water and filler.")
th("A good quality oil at six percent will beat a bargain bin oil at ten percent every single time.")
th("Second, be realistic about the room. No single candle scents an entire open-plan house, no matter what the marketing promises.")
br("No single candle scents an entire open-plan house, no matter what anyone promises you.","sets a single lit candle on a table in a large open-plan living space and steps back")
th("Room size, ceiling height, airflow, and open windows all fight against your throw. A small closed room will always smell stronger.")
th("Third, your wax brand and any dyes or additives change everything. Some additives actively suppress scent throw.")
th("If you are serious about throw, test one variable at a time. Change one thing, cure it, burn it, and take notes.")
# ===== ACT 8 the method =====
th("So before you ever reach for that bottle and pour in more oil, I want you to run through this real checklist instead.")
th("Number one. Weigh your fragrance to your wax's rated load on a scale, and do not exceed it. More is not better.")
th("Number two. Add that fragrance at around 185 degrees, and then stir gently for two full timed minutes.")
th("Number three. Right-size your wick so you get a full, edge-to-edge melt pool within a few hours of burning.")
th("Number four. And then cure that candle for at least two weeks before you let yourself judge it at all.")
br("Do those four things and your throw transforms, with the exact same amount of oil you already use.","lights a candle in a cozy warm room and settles back to enjoy it")
th("Do those four things, and I promise your scent throw transforms, using the exact same amount of oil you are already using.")
# ===== ACT 9 verdict + CTA =====
th("So here is the bottom line. Adding more fragrance oil is a band-aid, and most of the time it actively backfires on you.")
th("Fix the cure time, fix the temperature, fix the wick, and respect the load, and weak throw simply goes away on its own.")
th("It is not about more oil. It is about giving the oil you already have the chance to actually work.")
th("If this saved you from wasting money on more fragrance oil, do me a favor and subscribe, because I bust one of these candle myths every single week.")
th("And tell me down in the comments. What has your biggest scent-throw struggle been? I read every one, and I will try to help.")

# ---- build beats + gaps ----
def est(t): return max(1.5, round(len(t.split())/WPS+0.4,2))
beats=[]; gap=0; prev=None
for i,(typ,text,subj) in enumerate(B):
    if typ=="broll":
        if prev!="broll": gap+=1
        beats.append({"id":f"b{i:02d}_g{gap}","type":"broll","sentence":text,"visual_subject":subj,
                      "gap_id":gap,"prompt":hands_prompt(subj),"dur":est(text)})
    else:
        beats.append({"id":f"b{i:02d}_th","type":"character","sentence":text,"dur":est(text)})  # prompt set below
    prev=typ

# ---- split contiguous TH runs into chains of <=MAX_RUN; assign scenes ----
chains=[]; i=0; jump_idx=0; cid=0
while i<len(beats):
    if beats[i]["type"]!="character": i+=1; continue
    # gather a contiguous TH run
    run=[]; j=i
    while j<len(beats) and beats[j]["type"]=="character": run.append(beats[j]); j+=1
    # split into sub-chains of <=MAX_RUN
    for k in range(0,len(run),MAX_RUN):
        sub=run[k:k+MAX_RUN]
        is_jump = (k>0)                      # only a within-run split is a direct TH->TH jump-cut
        if is_jump:
            scene=JUMP_SCENES[jump_idx%len(JUMP_SCENES)]; jump_idx+=1
        else:
            scene="bench"
        seed=SCENES[scene]["anchor"]
        for pos,b in enumerate(sub):
            if pos==0:
                b["prompt"]=th_scene(b["sentence"],scene,moved=is_jump)
            else:
                b["prompt"]=th_continue(b["sentence"])
        chains.append({"id":cid,"scene":scene,"seed_keyframe_url":seed,
                       "beat_ids":[b["id"] for b in sub]}); cid+=1
    i=j

total=sum(b["dur"] for b in beats); th_t=sum(b["dur"] for b in beats if b["type"]=="character")
gaps=sorted(set(b["gap_id"] for b in beats if b["type"]=="broll"))
nth=sum(1 for b in beats if b["type"]=="character"); nbr=len(beats)-nth
jumps=sum(1 for c in chains if c["scene"]!="bench")
print(f"POOR SCENT THROW v2 | {len(beats)} beats ({nth} TH + {nbr} B-roll) | {len(chains)} chains "
      f"(max {MAX_RUN}/chain, {jumps} scene-change jump-cuts) | est {total/60:.1f} min | "
      f"TH ratio {th_t/total:.2f} | gaps(TTS)={len(gaps)}")
folder=os.path.join(ROOT,"..","video_ps_veo")
os.makedirs(os.path.join(folder,"Project files"),exist_ok=True); os.makedirs(os.path.join(folder,"Source clips"),exist_ok=True)
M={"title":"POOR SCENT THROW - Stop Adding More Fragrance, This Is The REAL Issue","channel":"Candice's Country Candles",
   "narrator_voice":VOICE,"aspect":"16:9","video_model":"veo-video","clip_len":8.0,"reference_photo_url":REF,
   "scenes":{k:v["anchor"] for k,v in SCENES.items()},"hands_ref_url":HANDS,"max_run":MAX_RUN,
   "continuity_bible":WS,"format":"th-dominant-chained-v5","chains":chains,"beats":beats,
   "gaps":{str(g):" ".join(b["sentence"] for b in beats if b.get("gap_id")==g) for g in gaps}}
json.dump(M,open(os.path.join(folder,"Project files","manifest.json"),"w"),indent=2)
print("wrote manifest.json")
