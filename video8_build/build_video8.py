#!/usr/bin/env python3
"""Video 8 — "I Tested The 'Microwave Your Wax' Hack — And It Ruined Everything"
NEW FORMAT: continuous channel VO; visual track alternates TALKING_HEAD (presenter,
own lip-synced audio) <-> B_ROLL (literal phone-cam depiction of the spoken noun, no
character). Informational/test, not tutorial. 7-act spine, unbelievable-claim hook.
Emits the beat-schedule table; writes the manifest. (Generation is launched only
after the table is approved.)"""
import json, os, math
ROOT=os.path.dirname(os.path.abspath(__file__))
REF=open("/tmp/raw_ref.txt").read().strip()

# ---- config knobs ----
CFG=dict(talking_head_ratio=0.40, max_th_run_s=10, max_broll_run_s=25,
         th_mode="sync", broll_beat_target_s=3, hook_archetype="unbelievable", clip_len=8.0)
VOICE={"provider":"elevenlabs","voiceId":"5u41aNhyCU6hXOcjPPv0","modelId":"eleven_multilingual_v2","speed":1.08}
WPS=2.7  # words/sec estimate at this voice+speed (for the review table)

WORLD=("An ordinary home kitchen and a small candle-making corner: a microwave on the counter, a "
"stovetop with a steel pot, glass candle jars, bags of soy wax flakes, a kitchen thermometer, "
"fragrance oil bottles, an electric wax melter, a heat gun. Everyday, lived-in, natural daylight.")
PHONE=("filmed as casual amateur smartphone footage: handheld iPhone video with slight natural "
"shake and minor reframing, eye-level or POV, natural available light (no studio lights), an "
"ordinary real-world kitchen setting, no color grading, slightly flat auto-exposed, deep focus "
"(NO cinematic shallow depth of field), candid vlog feel. No on-screen text, captions, watermark, "
"logos or title cards. Photo-real and physically correct; nothing spawns in or vanishes; hands "
"have five fingers; any liquid pours from a real container into a real open container.")
PERSON=("the exact same woman as the reference image: mid-fifties, tortoiseshell glasses, curly grey "
"hair, blue knit sweater, tan apron; identical every shot.")

def broll_prompt(subj, act, shot):
    return (f"{subj} {act} ({shot} shot), {PHONE} Setting: {WORLD}")
def th_prompt(line):
    return (f"Medium close handheld vlog shot of {PERSON} in her kitchen candle corner, looking "
    f"straight at the camera and speaking to it naturally in a warm American accent, lips fully in "
    f"sync, saying exactly: \"{line}\". Casual amateur smartphone look, natural window light, no "
    f"studio lighting, no on-screen text. Setting: {WORLD}")

# beat(type, text, subject, action, shot)  -- type 'th' or 'broll'
# Rule: true claims/transitions/authority/verdict/CTA -> TH; any line naming a concrete
# thing that can be shown -> B_ROLL (cut on the noun), VO continues over it.
B=[]
def th(text): B.append(("th",text,None,None,None,True))
def br(text,subj,act,shot="POV"): B.append(("broll",text,subj,act,shot,False))

# ===== FULL ~10 MIN SCRIPT (expanded) =====
# Strict alternation: no two TALKING_HEAD beats adjacent (keeps TH runs < max_th_run_s).
# TH = short direct address; B_ROLL carries the explanatory VO over literal footage.
# ===== ACT 1 — cold-open hook + scenario =====
th("Everyone online swears you can just microwave your candle wax to save time.")
br("So I tried that hack, in good faith, twelve different ways, and I filmed all of it.","a hand sliding a glass jar full of soy wax flakes into a microwave and pressing start","loading the jar, pressing start","POV")
th("And almost every single one of them ended in disaster.")
br("This one started smoking before the timer even hit a minute.","soy wax smoking inside a running microwave seen through the door","overheating and smoking","wide")
br("This jar cracked clean down the side.","a clear glass candle jar with a crack down the side on the turntable","cracked down the side","hero")
br("And this one came out scorched brown and smelling burnt.","a jar of brown overheated discoloured wax cooling on the counter","scorched brown wax","hero")
th("I have poured candles for fifteen years, and I really wanted this shortcut to work.")
br("Because thousands of people are following this exact advice right now, today.","a phone screen scrolling a short video captioned about microwaving wax","scrolling the hack video","POV")
th("And it is not just messy. It can be genuinely dangerous.")
# ===== ACT 2 — disarmer + rig =====
th("But I am not here to just dunk on a trend. I tested it properly.")
br("I clipped a kitchen thermometer straight into the wax for every single run.","a kitchen thermometer probe clipped into a jar of wax flakes","clipping the probe into the wax","hands")
br("And I wrote down the temperature every fifteen seconds.","a hand writing rising temperature numbers down a notebook column","writing the numbers down","hands")
th("Here is exactly what microwaving does to your wax, your jar, and your scent.")
# ===== ACT 3 — TEST 1 temperature / flash point =====
th("Test one. Temperature, and control.")
br("On the stove, the wax creeps up gently and levels off right around pour temp.","a thermometer in wax on a stove holding steady near a marked pour line","holding steady at pour temp","hands")
br("In the microwave, the reading just climbs and climbs, with nothing holding it back.","a thermometer in microwaving wax, the dial climbing fast","dial climbing fast","hands")
br("It blew past my safe pour temperature in under thirty seconds.","the thermometer needle pushing well past a marked pour line","needle past the pour line","hands")
th("And wax has a flash point. That is the temperature where it can actually catch fire.")
br("You can watch the smoke start lifting off the surface as it overheats.","thin wisps of smoke rising off a jar of overheated wax","smoke rising off the wax","hero")
br("A few seconds longer and that smoke turns into something you do not want near an open flame.","heavier smoke pouring off darkening wax in a jar","heavier smoke pouring off","hero")
# ===== ACT 4 — TEST 2 the jar =====
th("Test two. The jar itself.")
br("Glass heats unevenly in a microwave, with hot spots and cold spots side by side.","a glass jar of wax with visible heat shimmer rising off one side","uneven heat shimmer on the glass","hero")
br("That stress builds until a crack spreads right across the side.","a glass candle jar with a crack spreading across the side","a crack spreading across the glass","hero")
br("And then it splits, leaking hot wax, sometimes while it is still spinning inside.","a jar splitting and leaking hot wax onto the microwave turntable","leaking hot wax onto the turntable","wide")
th("Now imagine reaching in to grab that.")
br("I had to lift it out with a thick towel, and it was still far too hot to touch.","a hand lifting a leaking cracked jar with a folded kitchen towel","lifting the cracked jar with a towel","hands")
# ===== ACT 5 — TEST 3 the scent =====
th("Test three, and this is the one that really stings. The scent.")
br("Fragrance oil has its own heat ceiling, and above pour temp it simply burns off.","fragrance oil being poured from a bottle into a jar of very hot wax","pouring fragrance into hot wax","hands")
br("So you add your oil, it hisses, and half of it is gone before it ever mixes in.","fragrance oil hissing and steaming as it hits overheated wax","oil hissing on the hot wax","hero")
br("This microwaved candle burned a full hour, and you could barely smell it across the room.","a finished candle burning with a small flame, a hand fanning air, unimpressed","fanning the air, smelling nothing","reaction")
br("The stove-melted one filled the whole kitchen.","a similar candle burning while a person closes their eyes enjoying the scent","enjoying the strong scent","reaction")
# ===== ACT 5B — I tried different waxes =====
th("And before you say it was just my wax, no. I tried three.")
br("First, soy wax. It scorched and yellowed the fastest of the three.","a jar of soy wax turning yellow and scorched in a microwave","soy wax scorching yellow","hero")
th("Soy is soft and low-melt, so it punishes you the quickest.")
br("Then paraffin. It overheated so fast it started smoking almost immediately.","a jar of paraffin wax smoking heavily in a microwave","paraffin smoking immediately","hero")
th("And paraffin fumes when overheated are genuinely not something you want to breathe.")
br("Beeswax was the most stubborn, but it discoloured and smelled scorched too.","a jar of darkening beeswax with a scorched sheen in a microwave","beeswax darkening and scorching","hero")
th("Three different waxes, same machine, same sad result.")
# ===== ACT 5C — the science, simply =====
th("So here is what is actually going on, in plain English.")
br("A microwave heats unevenly, hammering little pockets of wax while others stay cold.","a cutaway jar of wax with bubbling hot pockets next to still-solid patches","hot pockets bubbling beside solid wax","hero")
br("Those overheated pockets rocket past the flash point while the rest is barely melted.","a thermometer in one bubbling pocket reading dangerously high","one pocket reading dangerously high","hands")
th("A water bath does the opposite. It shares the heat out, gently and evenly.")
br("Every part of the wax sits at the same calm temperature, all the way through.","an evenly melted pitcher of wax with a steady thermometer in a water bath","evenly melted, steady temperature","wide")
# ===== ACT 6 — why it happens / double boiler =====
th("So that is why the slow way wins so decisively.")
br("It comes down to one thing: control of the temperature.","a split scene of a microwave beside a gently steaming pot on a stove","microwave versus stovetop","wide")
br("The wax sits in a pitcher inside a pot of gently simmering water.","a steel pouring pitcher of wax standing in a pot of simmering water","standing in the water bath","wide")
br("Water cannot go much past a hundred degrees, so it warms the wax slowly and evenly.","gently simmering water bubbling around the base of the steel pitcher","water simmering around the pitcher","hands")
br("The thermometer just sits there, holding one steady, safe reading.","a thermometer in double-boiler wax holding one steady reading","holding a steady reading","hands")
th("You physically cannot blow past your pour temp. That is the entire point of it.")
br("And honestly, it only adds about ten quiet minutes to the whole process.","a calm wide shot of wax melting in a water bath while a kettle steams nearby","calm melting on the stovetop","wide")
# ===== ACT 7 — faster methods that DO work (long middle) =====
th("Now, if you genuinely want speed, three methods are actually faster, and still safe.")
br("All three give you the speed you wanted without any of the smoke or cracking.","three setups side by side on a counter: a bag of flakes, an electric melter, a heat gun","the three faster tools lined up","wide")
th("Method one. Flake your wax small.")
br("Snap the big blocks down into small flakes first.","a hand snapping a block of soy wax into small flakes on a board","snapping wax into flakes","hands")
br("Small pieces melt in about half the time, with all of the control.","small wax flakes melting quickly in a steel pitcher in a water bath","flakes melting quickly","wide")
th("Method two. A cheap electric wax melter.")
br("It is basically a little pot with a temperature dial built in.","an electric wax melter with a temperature dial sitting on a counter","melter with its dial lit","hero")
br("You dial in your temperature, and it holds it for you, exactly.","a hand turning the dial on the electric melter to a set point","turning the dial to a set point","hands")
br("Set it, walk away, and come back to a pot of perfectly melted wax.","smooth melted wax sitting still and even inside the electric melter","wax held smooth and steady","wide")
th("Method three. Finish stubborn lumps with a heat gun.")
br("Melt most of the batch gently on the stove.","a pitcher of mostly melted wax with a few solid lumps still floating","a few lumps left floating","hands")
br("Then warm the last few lumps with a heat gun until they vanish.","a heat gun warming the last solid lumps in the pitcher until they melt","heat gun melting the last lumps","hands")
br("And you pour it clean and smooth into an open jar, no cracks, no smoke.","smooth melted wax pouring from a pitcher into an open glass jar","pouring smoothly into the open jar","hands")
th("Any one of those beats babysitting a microwave and then scraping out a cracked jar.")
# ===== ACT 7B — the pour-temperature cheat sheet =====
th("And since we are here, let me save you the guesswork on temperature.")
br("Soy wax pours nicely somewhere around one hundred and thirty-five degrees.","a thermometer in pale soy wax reading about one hundred and thirty-five","soy wax at pour temp","hands")
br("Paraffin likes it a touch hotter, and beeswax hotter still.","two jars of wax side by side with thermometers at different readings","paraffin and beeswax pour temps","hands")
th("But the rule is the same for all of them: melt high, then let it cool to pour temp.")
br("You melt the wax fully, then you wait and watch it drift down to your number.","a hand holding a thermometer in cooling wax, the reading slowly dropping","watching the wax cool to pour temp","hands")
th("That cooling window is exactly the control a microwave never gives you.")
# ===== ACT 7C — what the pros actually do + the real mistake =====
th("Here is what people who sell candles every week actually do.")
br("They melt low and slow, and they keep a thermometer in the wax the entire time.","a steady melting pitcher with a thermometer left sitting in it on a stove","thermometer left in the whole time","wide")
br("Fragrance goes in only once the wax has cooled to pour temp, never before.","a hand pouring fragrance oil into wax at a calm, lower temperature","adding fragrance at pour temp","hands")
th("And the single biggest mistake, even on the stove, is rushing that cooldown.")
br("Pour too hot and you get sinkholes and a weak scent, even with a perfect melt.","a cooled candle with a deep sinkhole around the wick","sinkhole from pouring too hot","hero")
th("Patience is not the fun part, but it is the part that actually works.")
# ===== ACT 8 — verdict + soft CTA =====
th("So, the final verdict on the microwave wax hack.")
br("Cracked jars, scorched wax, and dead fragrance.","a cracked scorched microwaved jar of dull wax on the counter","the ruined microwaved jar","hero")
br("Versus a clean, glossy candle that actually smells incredible.","a flawless cream candle with a glossy top burning with a strong steady flame","the perfect stovetop candle","hero")
th("Please, just skip the microwave. The double boiler exists for a very good reason.")
br("Slow and steady really does win this one, every single time.","two hands setting a finished glossy candle gently onto a shelf of candles","placing the finished candle on the shelf","hands")
th("If this saved you a ruined batch, subscribe, because I put one of these hacks on trial every week.")
br("These are the hacks lined up on the bench for testing next.","a row of handwritten note cards of candle hack ideas on a kitchen table","panning across the next hack ideas","wide")
th("Tell me in the comments which one I should put on trial first.")

# ---- build beat objects with estimated durations + scheduler audit ----
def est(text): return max(1.4, round(len(text.split())/WPS+0.4,2))
beats=[]; t=0.0
for i,(typ,text,subj,act,shot,abs_) in enumerate(B):
    d=est(text);
    bid=f"b{i:02d}_{'th' if typ=='th' else 'br'}"
    prompt = th_prompt(text) if typ=="th" else broll_prompt(subj,act,shot)
    beats.append({"id":bid,"type":"character" if typ=="th" else "broll","sentence":text,
                  "prompt":prompt,"visual_subject":subj,"visual_action":act,"shot_type":shot,
                  "abstract":abs_,"t_start":round(t,2),"t_end":round(t+d,2),"dur":d})
    t+=d
total=t
th_time=sum(b["dur"] for b in beats if b["type"]=="character")
# run-length audit
def runs():
    longest_th=longest_br=cur=0; curtype=None
    for b in beats:
        if b["type"]==("character" if curtype=="th" else "broll") and curtype:
            pass
    # simple consecutive run calc
    lt=lb=0; run=0; prev=None
    for b in beats:
        k="th" if b["type"]=="character" else "br"
        if k==prev: run+=b["dur"]
        else: run=b["dur"]; prev=k
        if k=="th": lt=max(lt,run)
        else: lb=max(lb,run)
    return lt,lb
lt,lb=runs()

# ---- emit beat-schedule table ----
print(f"VIDEO #8 — Microwave Wax Hack | {len(beats)} beats | est {total/60:.1f} min")
print(f"talking-head ratio = {th_time/total:.2f} (target {CFG['talking_head_ratio']}) | "
      f"longest TH run {lt:.1f}s (max {CFG['max_th_run_s']}) | longest B_ROLL run {lb:.1f}s (max {CFG['max_broll_run_s']})")
print("="*100)
print(f"{'#':>3} {'t_start–t_end':>14} {'type':<11} subject / line")
print("-"*100)
for i,b in enumerate(beats):
    rng=f"{b['t_start']:.1f}-{b['t_end']:.1f}"
    if b["type"]=="character":
        print(f"{i:>3} {rng:>14} {'TALKING_HEAD':<11} \"{b['sentence'][:62]}\"")
    else:
        print(f"{i:>3} {rng:>14} {'B_ROLL':<11} {b['visual_subject'][:40]} | {b['visual_action'][:28]} [{b['shot_type']}]")
print("="*100)
print("source: TALKING_HEAD=Veo mode-A lip-synced (own audio); B_ROLL=Veo mode-B phone-cam (VO over)")

# ---- write manifest (used only after approval) ----
folder=os.path.join(ROOT,"..","video8_veo"); os.makedirs(os.path.join(folder,"Project files"),exist_ok=True); os.makedirs(os.path.join(folder,"Source clips"),exist_ok=True)
M={"title":"I Tested The Microwave Your Wax Hack - And It Ruined Everything",
   "channel":"Candice's Country Candles","narrator_voice":VOICE,"aspect":"16:9","video_model":"veo-video",
   "clip_len":8.0,"reference_photo_url":REF,"continuity_bible":WORLD,"format":"talking-head<->phone-cam-broll","config":CFG,"beats":beats}
json.dump(M,open(os.path.join(folder,"Project files","manifest.json"),"w"),indent=2)
