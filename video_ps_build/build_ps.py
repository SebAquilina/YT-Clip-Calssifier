#!/usr/bin/env python3
"""POOR SCENT THROW: Stop Adding More Fragrance — This Is The REAL Issue
Talking-head-dominant informational video (FORMAT v4): chained talking heads carry
their own audio; rare critical B-roll; one TTS per gap; new TTS voice."""
import json, os
ROOT=os.path.dirname(os.path.abspath(__file__))
REF=open("/tmp/raw_ref.txt").read().strip()
THKF=open("/tmp/th_startframe_url.txt").read().strip()
VOICE={"provider":"elevenlabs","voiceId":"uTof433lKWylEy1elPTY","modelId":"eleven_multilingual_v2","speed":1.05}
WPS=2.7
WS=("an ordinary lived-in home candle workshop kitchen: a worktable, glass candle jars, bags of soy "
"wax, amber fragrance-oil bottles, a kitchen thermometer, a small scale, a stovetop pot and a "
"curing shelf of finished candles, natural daylight.")
PHONE=("filmed as casual amateur smartphone footage: handheld, slight natural shake, eye-level or POV, "
"natural available light, no studio lights, no color grading, slightly flat auto-exposed, deep focus, "
"candid vlog feel. No on-screen text, captions, watermark or logos. Photo-real and physically correct; "
"nothing spawns in or vanishes; hands have five fingers; continuous subtle camera motion, never a "
"frozen frame.")
PERSON=("the exact same woman as the reference image: mid-fifties, tortoiseshell glasses, curly grey "
"hair, blue knit sweater, tan apron.")
TH_STRICT=("Exactly ONE person, a single solid subject — no second face, no double exposure, no "
"ghosting, no morphing, no extra hands; natural blink and lip-sync; steady framing; natural window "
"light only. The first frame is already this exact woman, sharp and in focus, no fade-in or morph. "
"She is already mid-conversation: begins the first word immediately with no inhale or pause, speaks "
"continuously without freezing, no big inhale at the end.")
def th_prompt(line):
    return (f"Continue from the reference start image: the same woman in the same kitchen, same pose and "
    f"framing, looking straight at the camera, speaking naturally in a warm American accent, lips fully "
    f"in sync, saying exactly: \"{line}\". {TH_STRICT} Casual handheld smartphone vlog look. Setting: {WS}")
def br_prompt(subj,mode):
    if mode=="character":
        return (f"Starting from the reference image, {PERSON} {subj}. {PHONE} She is doing the action, not "
        f"speaking to camera; show hands and the action. Setting: {WS}")
    return (f"{subj}. {PHONE} Setting: an ordinary real-world candle kitchen. No channel character needed.")
B=[]
def th(t): B.append(("th",t,None,None))
def br(t,subj,mode="generic"): B.append(("broll",t,subj,mode))

# ===== ACT 1 hook =====
th("If your candles have a weak scent throw, I already know exactly what you are about to do. You are about to add more fragrance oil.")
th("Please, stop right there. That is the single most common mistake I see, and nine times out of ten it makes the problem worse, not better.")
th("I have made candles for fifteen years, and I promise you the answer is almost never just more oil.")
th("By the end of this video you are going to understand the real reasons a candle does not throw, and how to actually fix every one of them.")
br("You light a beautiful candle, lean in close, and barely smell a thing.","a person leaning over a freshly lit candle, sniffing, looking disappointed","generic")
th("It is one of the most frustrating things in this whole hobby. You did everything right, and the room still smells like nothing.")
# ===== ACT 2 the myth / max load =====
th("So before we fix anything, let me kill the myth at the center of all of this.")
th("Scent throw is not simply more oil equals more smell. That is just not how wax chemistry works.")
th("Every single wax has a maximum fragrance load. It is the most oil that wax can actually hold and bind to.")
th("For most soy waxes that ceiling is somewhere around eight to ten percent of the wax weight.")
br("Ten percent is the ceiling, and you measure it on a scale, not by eye.","a small digital scale with a jar of wax and an amber oil bottle, the display showing a weight","generic")
th("Your wax supplier publishes that number. It is on the spec sheet, and it is worth looking up before you pour anything.")
th("Now here is what happens when you ignore it and go past that ceiling.")
th("The wax physically cannot hold the extra oil. There is simply nowhere left for it to bind inside the wax.")
br("So it leaches back out and pools as oily sweat on top of the candle.","a finished candle with shiny oily beads of fragrance sweating on its surface","generic")
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
br("That is why serious makers cure every candle on a shelf for a week or two before they ever sell it.","a slow pan along a shelf of curing candles, a small handwritten date tag beside one","generic")
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
br("The sweet spot is right around 185 degrees, checked with a thermometer, not guessed.","a kitchen thermometer in melted wax reading about 185 degrees, a hand adding fragrance oil","generic")
th("For most soy wax, the sweet spot is right around 185 degrees Fahrenheit. Check your specific wax, but that is the ballpark.")
th("And please, use an actual thermometer. Guessing by eye is how you end up forty degrees off without ever knowing it.")
th("Once you hit that temperature, add your fragrance, and then stir gently and steadily for a full two minutes.")
br("Two full minutes of slow stirring is what actually locks the oil into the wax.","a hand slowly stirring fragrance into a pitcher of melted wax with a spatula","generic")
th("I know two minutes feels like forever when you are standing there stirring. Time it on your phone anyway.")
th("Rush that stir, and half your fragrance never properly bonds with the wax. It is the most skipped step in all of candle making.")
# ===== ACT 5 wick / melt pool =====
th("Real issue number three, and almost nobody talks about this one. Your wick.")
th("This sounds unrelated to scent, but it is one of the biggest factors of all. Let me explain why.")
th("When a candle burns, the scent does not come from the wax sitting there cold. It comes from the melt pool.")
th("The melt pool is that pool of hot liquid wax that forms around the flame. That is where the fragrance evaporates from.")
br("A wick that is too small makes a tiny flame and a tiny melt pool, so barely any scented wax is being warmed.","a candle burning with a small flame and only a narrow ring of melted wax, the rest still solid","generic")
th("So if your wick is too small, you get a tiny flame, and only a thumbnail of wax ever melts.")
th("That means only that tiny bit of fragrance is being warmed and released into the room. The rest of your scent is locked in solid wax.")
th("You could have the best oil in the world at the perfect load, and a too-small wick will still strangle the throw.")
th("The fix is to size your wick to your jar, so the melt pool reaches the edges within a few hours of burning.")
br("A full, edge-to-edge melt pool releases far more scent than any amount of extra oil ever could.","a candle burning with a wide full melt pool of liquid wax right to the edges of the jar","generic")
th("Honestly, going up just one wick size will usually do more for your throw than adding two percent more fragrance ever would.")
th("So before you touch the oil, ask yourself if your candle is even reaching a full melt pool.")
# ===== ACT 6 cold vs hot throw =====
th("Now there is one more thing I need you to get straight, because people judge candles wrong all the time.")
th("You need to know which kind of throw you are even measuring. There are two, and they are completely different.")
th("Cold throw is the scent you get when the candle is sitting there unlit. Hot throw is the scent when it is actively burning.")
br("Some oils smell incredible cold in the jar, and then go strangely quiet once they are lit.","a hand lifting an unlit candle to the nose, then the same candle shown burning","generic")
th("Some fragrance oils are amazing cold and disappointing hot. Others are the complete opposite. It depends on the oil.")
th("So do not throw out a recipe just because the cold throw is shy. Light it, let it reach a full pool, and then judge the hot throw.")
th("Judging a candle by sniffing the cold jar is like judging a meal by smelling the raw ingredients. You have to actually cook it.")
# ===== ACT 7 other truths =====
th("Alright, a few more quick truths, and every one of these matters more than dumping in extra oil.")
th("First, cheap fragrance oil is very often just weak fragrance oil. You are paying for water and filler.")
th("A good quality oil at six percent will beat a bargain bin oil at ten percent every single time.")
th("Second, be realistic about the room. No single candle scents an entire open-plan house, no matter what the marketing promises.")
br("No single candle scents an entire open-plan house, no matter what anyone promises you.","a single candle burning on a table in a large open-plan living space","generic")
th("Room size, ceiling height, airflow, and open windows all fight against your throw. A small closed room will always smell stronger.")
th("Third, your wax brand and any dyes or additives change everything. Some additives actively suppress scent throw.")
th("If you are serious about throw, test one variable at a time. Change one thing, cure it, burn it, and take notes.")
# ===== ACT 8 the method =====
th("So before you ever reach for that bottle and pour in more oil, I want you to run through this real checklist instead.")
th("Number one. Weigh your fragrance to your wax's rated load on a scale, and do not exceed it. More is not better.")
th("Number two. Add that fragrance at around 185 degrees, and then stir gently for two full timed minutes.")
th("Number three. Right-size your wick so you get a full, edge-to-edge melt pool within a few hours of burning.")
th("Number four. And then cure that candle for at least two weeks before you let yourself judge it at all.")
br("Do those four things and your throw transforms, with the exact same amount of oil you already use.","a cozy warm room with a single candle burning, someone settling into a couch nearby","generic")
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
for i,(typ,text,subj,mode) in enumerate(B):
    if typ=="broll":
        if prev!="broll": gap+=1
        beats.append({"id":f"b{i:02d}_g{gap}","type":"broll","sentence":text,"visual_subject":subj,
                      "broll_mode":mode,"gap_id":gap,"prompt":br_prompt(subj,mode),"dur":est(text)})
    else:
        beats.append({"id":f"b{i:02d}_th","type":"character","sentence":text,"prompt":th_prompt(text),"dur":est(text)})
    prev=typ
total=sum(b["dur"] for b in beats); th_t=sum(b["dur"] for b in beats if b["type"]=="character")
gaps=sorted(set(b["gap_id"] for b in beats if b["type"]=="broll"))
nth=sum(1 for b in beats if b["type"]=="character"); nbr=len(beats)-nth
print(f"POOR SCENT THROW | {len(beats)} beats ({nth} TH + {nbr} B-roll) | est {total/60:.1f} min | TH ratio {th_t/total:.2f} | gaps(TTS)={len(gaps)}")
folder=os.path.join(ROOT,"..","video_ps_veo"); os.makedirs(os.path.join(folder,"Project files"),exist_ok=True); os.makedirs(os.path.join(folder,"Source clips"),exist_ok=True)
M={"title":"POOR SCENT THROW - Stop Adding More Fragrance, This Is The REAL Issue","channel":"Candice's Country Candles",
   "narrator_voice":VOICE,"aspect":"16:9","video_model":"veo-video","clip_len":8.0,"reference_photo_url":REF,
   "th_keyframe_url":THKF,"continuity_bible":WS,"format":"th-dominant-chained","beats":beats,
   "gaps":{str(g):" ".join(b["sentence"] for b in beats if b.get("gap_id")==g) for g in gaps}}
json.dump(M,open(os.path.join(folder,"Project files","manifest.json"),"w"),indent=2)
