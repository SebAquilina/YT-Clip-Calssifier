#!/usr/bin/env python3
"""Video 8 v2 — "I Tested The 'Microwave Your Wax' Hack" — talking-head-DOMINANT
(~70%) informational rebuild. Talking heads carry their own audio; B-roll is rare
and only for critical proof shots (generic clip or character doing the thing).
Consecutive B-roll beats are grouped into GAPS -> ONE TTS per gap (not per beat)."""
import json, os
ROOT=os.path.dirname(os.path.abspath(__file__))
REF=open("/tmp/raw_ref.txt").read().strip()
CFG=dict(talking_head_ratio=0.70, max_th_run_s=999, max_broll_run_s=20, clip_len=8.0)
VOICE={"provider":"elevenlabs","voiceId":"5u41aNhyCU6hXOcjPPv0","modelId":"eleven_multilingual_v2","speed":1.06}
WPS=2.7

KITCHEN=("an ordinary lived-in home kitchen with a candle-making corner: a microwave on the "
"counter, a stovetop with a steel pot, glass candle jars, bags of soy wax, a kitchen thermometer, "
"fragrance oil bottles, an electric wax melter and a heat gun, natural daylight.")
PHONE=("filmed as casual amateur smartphone footage: handheld, slight natural shake, eye-level or "
"POV, natural available light, no studio lights, no color grading, slightly flat auto-exposed, "
"deep focus (no cinematic shallow depth of field), candid vlog feel. No on-screen text, captions, "
"watermark or logos. Photo-real and physically correct; nothing spawns in or vanishes; hands have "
"five fingers; liquids pour from a real container into a real open container.")
PERSON=("the exact same woman as the reference image: mid-fifties, tortoiseshell glasses, curly grey "
"hair, blue knit sweater, tan apron.")
TH_STRICT=("Exactly ONE person, a single solid subject — no second transparent copy, no double "
"exposure, no ghosting, no morphing, no extra or duplicated hands or arms; natural blink and "
"lip-sync; steady framing; only natural window light, no studio lighting, no glow.")
def th_prompt(line):
    return (f"Medium close handheld vlog shot of {PERSON} in her kitchen, looking straight at the "
    f"camera and speaking naturally in a warm American accent, lips fully in sync, saying exactly: "
    f"\"{line}\". {TH_STRICT} Casual smartphone look. Setting: {KITCHEN} No on-screen text.")
def br_prompt(subj, mode):
    if mode=="character":
        return (f"Starting from the reference image, {PERSON} {subj}. {PHONE} She is doing the action, "
        f"not speaking to camera; show her hands and the action. Setting: {KITCHEN}")
    return (f"{subj}. {PHONE} Setting: an ordinary real-world kitchen. No channel character needed.")

B=[]
def th(t): B.append(("th",t,None,None))
def br(t,subj,mode="generic"): B.append(("broll",t,subj,mode))  # t=VO line, subj=visual

# ===== informational, talking-head-led =====
th("Everyone online keeps telling you to just microwave your candle wax to save a few minutes.")
th("I am going to show you exactly why that is one of the worst shortcuts in candle making.")
th("I have poured candles for fifteen years, and I tested this hack twelve different ways so you do not have to.")
br("And almost every single attempt ended in a small disaster.","soy wax smoking inside a running microwave seen through the glass door","generic")
br("Cracked jars, scorched brown wax, and a kitchen that smelled like burning chemicals.","a cracked glass jar of dark scorched wax sitting on a kitchen counter","generic")
th("So let me walk you through what is actually happening, because once you see it, you will never do this again.")
th("The entire problem comes down to a single word. Control.")
th("On a stove, you melt wax in a double boiler, which is just a pot of water with your wax pitcher sitting in it.")
th("And water has a hard ceiling. It physically cannot get much past a hundred degrees.")
br("So the wax just sits there, holding a calm, steady, safe temperature the whole time.","a kitchen thermometer in a pitcher of wax in a simmering water bath, holding one steady reading","generic")
th("A microwave has none of that safety. It dumps energy straight into the wax with nothing holding it back.")
br("So the temperature does not gently climb. It rockets, straight past the point where wax can catch fire.","a thermometer in microwaving wax, the needle shooting past a marked pour line","generic")
th("Because wax has a flash point. That is the temperature where it can actually ignite, right there in your kitchen.")
br("And you can watch the smoke start lifting off the surface as it breaks down.","thin wisps of smoke rising off a jar of overheated wax","generic")
th("That smoke is your wax and your fragrance literally cooking apart. It is a real fire risk, not a dramatic one.")
th("And here is the science of why, in plain English.")
th("A microwave does not heat evenly. It hammers tiny pockets of the wax while the wax right next to them stays solid.")
br("So one pocket is boiling and smoking while the rest is barely soft. There is no even, gentle melt.","a cutaway jar of wax with one violently bubbling hot pocket beside still-solid wax","generic")
th("A water bath does the exact opposite. It shares heat slowly and evenly through the whole batch.")
th("And do not think it was just my wax. I tried three different kinds, and they all failed.")
th("Soy is soft and low-melt, so it scorched and yellowed the fastest of the three.")
th("Paraffin overheated so quickly it was smoking almost immediately, and those fumes are genuinely nasty.")
th("Beeswax was the most stubborn, but it still darkened and picked up a burnt smell.")
th("Three waxes, one microwave, the same sad result every time.")
th("Then there is the jar itself, and this one surprises people.")
th("Glass does not heat evenly in a microwave. One side gets blistering hot while the other stays cool.")
br("That uneven stress builds until a crack spreads right across the glass, and it splits.","a clear glass candle jar developing a crack across the side and splitting","generic")
th("I had jars crack while they were still spinning inside. Now picture reaching in to grab that.")
th("And here is the part that really stings, even if you get lucky and nothing breaks.")
th("Fragrance oil has its own heat ceiling. Push the wax past pour temperature and the scent just cooks off.")
br("You add your oil, it hisses against the overheated wax, and half of it is gone before it even mixes in.","fragrance oil being poured into a jar of very hot wax, hissing and steaming","generic")
th("So you end up with a candle that looks perfectly fine, and then barely smells like anything when you light it.")
th("Now, I am not telling you to suffer with a slow stove if your time is tight. You have real options.")
th("Option one. Flake your wax down small. Smaller pieces melt in about half the time, with full control.")
th("Option two. A cheap electric wax melter with a temperature dial. You set your number, and it simply holds it.")
th("Option three. Melt most of the batch gently, then finish the last stubborn lumps with a heat gun.")
br("Any of those gets you real speed without the smoke, the cracking, or the dead fragrance.","a hand pouring smooth clean melted wax from a pitcher into an open glass jar","generic")
th("And while we are here, let me give you the temperature numbers that actually matter.")
th("Soy wax pours best around a hundred and thirty-five degrees. Paraffin a touch hotter, beeswax hotter still.")
th("But the rule is the same for all of them. Melt it fully, then let it cool down to your pour temperature.")
br("That cooling window, watching the thermometer drift down to your number, is exactly the control a microwave erases.","a hand holding a thermometer in cooling wax, the reading slowly dropping toward a marked line","generic")
th("It is what every candlemaker who sells their work actually does. Low, slow, and a thermometer in the wax the whole time.")
# ---- the 12 attempts / data ----
th("Now I promised you I tested this twelve different ways, so let me tell you what I actually tried.")
th("I tried short bursts. Thirty seconds, stir, thirty more. People swear this is the safe way to do it.")
th("It is better than one long blast, but the wax still overheated in patches, and it took longer than the stove.")
th("I tried low power settings. Half power, then a third power, thinking I could baby it along.")
th("The wax just heated slower and more unevenly. I still got hot spots, I just waited longer to get them.")
th("I tried covering the jar, uncovering the jar, different jar shapes, thick glass, thin glass.")
br("Every single thick-versus-thin glass test ended the same way, with a crack somewhere in the jar.","two glass jars side by side, one thick one thin, each with a crack across it","generic")
th("I even tried tiny amounts, just a few ounces at a time, to keep it controllable.")
th("And honestly, that was the only version that did not actively fail, but at that point you are microwaving wax all afternoon.")
th("Out of twelve attempts, I got exactly zero candles I would ever sell or even gift.")
th("Twelve tries, and the boring double boiler beat every one of them on the very first go.")
# ---- related stove mistakes ----
th("Now I do not want you to think the stove makes you bulletproof, because you can still mess this up.")
th("The single biggest mistake people make, even on the stove, is pouring while the wax is still too hot.")
br("Pour too hot and the candle sinks in the middle as it cools, leaving an ugly crater around the wick.","a cooled candle with a deep sinkhole crater around the central wick","generic")
th("Pour too hot and you also get those cloudy wet spots where the wax shrinks away from the glass.")
th("So the lesson is the same either way. It was never really about the microwave. It is about temperature control.")
# ---- myths ----
th("While we are at it, let me knock down a few related myths I hear constantly.")
th("Myth one. Hotter wax means a stronger scent. It is the opposite. Too hot, and you burn the fragrance off.")
th("Myth two. You can speed up cooling in the freezer. Do that and you will crack the jar and frost the top.")
th("Myth three. If it looks melted, it is ready to pour. Looks mean nothing. Only the thermometer tells the truth.")
br("A jar that looks perfectly melted on top can still be way too hot underneath, like this one.","a thermometer dipped into smooth-looking melted wax reading alarmingly high","generic")
# ---- beginner advice ----
th("So if you are just starting out, here is the whole thing in one breath.")
th("Melt low and slow in a water bath. Keep a thermometer in the wax. Let it cool to pour temp before the fragrance goes in.")
th("Do that, and you will outperform every microwave shortcut on the internet, every single time.")
# ---- the money cost ----
th("Let me put a real number on this, because that is what finally changed my mind.")
th("A ruined jar of wax with fragrance in it can easily cost you five or six dollars, gone in one bad minute.")
th("Do that twice a week while you are learning, and the microwave hack quietly costs you hundreds a year.")
br("That is a whole shelf of candles you could have sold, sitting in the bin instead.","a bin with several cracked jars and scorched wax beside an empty candle display shelf","generic")
th("Compared to that, ten extra minutes at the stove is the cheapest insurance in the whole craft.")
# ---- why the myth spreads ----
th("So why does this hack spread everywhere if it is so bad?")
th("Because it half works on something else entirely. Melting a tiny bit of leftover wax for wax melts.")
th("A spoonful of wax in a microwave-safe dish, in short bursts, with no jar and no fragrance, is mostly fine.")
br("Like this, a little dish of plain wax for a warmer, melted in a few short bursts.","a small microwave-safe dish of a little plain wax melting gently in short bursts","generic")
th("People do that once, it works, and then they wrongly assume it scales up to a full fragranced jar candle. It does not.")
# ---- judging temperature / thermometer ----
th("Now you might be wondering, can I just eyeball the temperature instead of buying a thermometer?")
th("Honestly, no. Wax gives you almost no visual warning before it is way too hot.")
th("A four dollar kitchen thermometer is the single best tool you can buy, and it pays for itself in one saved batch.")
# ---- storing / reusing wax ----
th("And do not toss your leftover melted wax either. Let it set in the pitcher and re-melt it next time, gently.")
th("Wax does not really go off. What kills it is overheating, the exact thing the microwave guarantees.")
# ---- two more myths ----
th("Two last myths before the verdict.")
th("Myth. Stirring while you microwave fixes the hot spots. It helps a little, but you are still flying blind on temperature.")
th("Myth. A microwave-safe jar is microwave-safe with wax in it. The wax is the problem, not the glass rating.")
th("So here is my honest verdict on the microwave hack.")
th("It saves you maybe ninety seconds, and in exchange it can cost you the jar, the wax, and the scent.")
br("A cracked, scorched mess on one side, and a clean, glossy, great-smelling candle on the other.","a cracked scorched jar beside a flawless glossy finished candle on a counter","generic")
th("The double boiler has been around forever for a reason. Slow and steady genuinely wins this one.")
th("If this saved you from ruining a batch, subscribe, because I put one of these hacks on trial every week.")
th("And tell me down in the comments which candle hack you want me to test next.")

# ---- build beats + gap grouping ----
def est(t): return max(1.5, round(len(t.split())/WPS+0.4,2))
beats=[]; gap=0; prev=None
for i,(typ,text,subj,mode) in enumerate(B):
    if typ=="broll":
        if prev!="broll": gap+=1
        bid=f"b{i:02d}_g{gap}"
        beats.append({"id":bid,"type":"broll","sentence":text,"visual_subject":subj,"broll_mode":mode,
                      "gap_id":gap,"prompt":br_prompt(subj,mode),"dur":est(text)})
    else:
        bid=f"b{i:02d}_th"
        beats.append({"id":bid,"type":"character","sentence":text,"prompt":th_prompt(text),"dur":est(text)})
    prev=typ
total=sum(b["dur"] for b in beats); th_t=sum(b["dur"] for b in beats if b["type"]=="character")
gaps=sorted(set(b["gap_id"] for b in beats if b["type"]=="broll"))
nth=sum(1 for b in beats if b["type"]=="character"); nbr=len(beats)-nth
print(f"VIDEO #8 v2 | {len(beats)} beats ({nth} TH + {nbr} B-roll) | est {total/60:.1f} min")
print(f"talking-head ratio = {th_t/total:.2f} (target 0.70) | gaps (=TTS clips) = {len(gaps)} | B-roll clips = {nbr}")
print(f"TTS calls = {len(gaps)} (one per gap)  vs old per-beat = {nbr}")
# write manifest
folder=os.path.join(ROOT,"..","video8b_veo"); os.makedirs(os.path.join(folder,"Project files"),exist_ok=True); os.makedirs(os.path.join(folder,"Source clips"),exist_ok=True)
M={"title":"I Tested The Microwave Your Wax Hack - And It Ruined Everything","channel":"Candice's Country Candles",
   "narrator_voice":VOICE,"aspect":"16:9","video_model":"veo-video","clip_len":8.0,"reference_photo_url":REF,
   "continuity_bible":KITCHEN,"config":CFG,"format":"th-dominant-gap-tts","beats":beats,
   "gaps":{str(g):" ".join(b["sentence"] for b in beats if b.get("gap_id")==g) for g in gaps}}
json.dump(M,open(os.path.join(folder,"Project files","manifest.json"),"w"),indent=2)
