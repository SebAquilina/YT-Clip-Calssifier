#!/usr/bin/env python3
"""Build BOTH manifests for video 2 — "Candle Defects You Can Fix WITHOUT
Repouring — In 30 Seconds Each" — same script/scenes, one 100% Veo, one 100%
Grok. Narration is identical across both (generated once, shared) so the user can
compare the engines' visuals directly. Prompts are tailored per engine:
  - Veo: the five-block structure (action + iPhone + person + world + realism/neg)
  - Grok: natural-language scene description + named camera move + physics stated
    as plain clauses (per xAI/Grok guidance).
Each beat carries an action_type that injects the matching SCENE physics block."""
import json, os
ROOT=os.path.dirname(os.path.abspath(__file__))
REF=open("/tmp/raw_ref.txt").read().strip()

WORLD=("A cozy home candle workshop: a rustic reclaimed-wood worktable; wooden shelves "
"behind lined with amber fragrance bottles, pale soy wax and rows of finished cream candles "
"in clear glass jars; a bright window with soft natural daylight; a heat gun, small scissors, "
"a wick bar, cotton and wood wicks, twine and dried botanicals on the table. The maker is a "
"friendly woman in her fifties with curly grey hair, tortoiseshell glasses, a blue knit sweater "
"and a tan canvas apron. Warm creams, honey amber, soft wood browns; bright natural light.")
IPHONE=("Filmed casually on a modern smartphone, wide ~26mm lens, deep focus, natural window "
"daylight, slight handheld micro-shake, true-to-life color; no bokeh, no film grain, no grade.")
PERSON=("Whenever a person appears she is the exact same woman as the reference image; identical "
"face, hair, glasses, blue sweater and tan apron in every shot.")
GLOBAL=("Object permanence: everything visible at the start stays present and consistent; nothing "
"appears or vanishes; shelf items stay put; the apron and sweater are already on from the first "
"frame and never snap on or change; hands have five fingers and hold tools correctly; no readable "
"text — jars are unlabeled or wear a plain kraft label with no legible words.")
SCENE={
 "pour":"The destination jar is OPEN and lidless; a continuous stream leaves the spout and lands INSIDE the open jar and the level rises; never a lid or cap on the jar, never liquid through a closed top.",
 "trim":"A single wick is clearly present and upright; the blades close ON the wick and cut at its tip; the cut piece falls; the wick stays rooted; never cut empty air or wax.",
 "center":"An actual wick is present; the wick bar or clip straddles and gently holds THAT wick across the jar rim, the wick visible and centered; never a clip holding nothing.",
 "heatgun":"The heat gun is held a few inches above the wax and points down at the surface; the top visibly melts smooth and level; the tool is real and present throughout; no floating tool, no instant jump.",
 "toppings":"Dried botanicals rest on the wax surface and are gently pressed and melted in so they stay embedded; nothing floats, multiplies or vanishes.",
 "label":"A plain kraft label (no legible words) is peeled and smoothed straight onto the jar; the hand moves it continuously; never teleported.",
 "defect":"A static, honest look at the flaw; nothing is being changed yet; everything physically stable.",
 "result":"A clean finished candle, physically stable, nothing changing or appearing.",
 "scene":"Everything physically stable and continuous; nothing appears or disappears.",
}
def NEG(): return ("NEGATIVE: no lid on an open jar, no liquid through a closed top, no cutting empty "
"air, no clip holding nothing, no floating tools, nothing spawning in or vanishing, no clothing "
"snapping on, no extra or fused fingers, no warped faces, no gibberish or warped text.")
def veo(action,at): return f"{action} {SCENE[at]} {IPHONE} {PERSON} World: {WORLD} GLOBAL: {GLOBAL} {NEG()}"
def grok(action,at,cam):
    return (f"{action} {cam}. Soft natural window light in a cozy rustic candle workshop, warm tones, "
    f"photoreal handheld smartphone look. {SCENE[at]} The same grey-haired woman in glasses, blue "
    f"sweater and tan apron whenever she appears, identical each time. Everything stays physically "
    f"real and continuous: {GLOBAL}")

def B(id,sent,action,at,cam): return {"id":id,"at":at,"sentence":sent,
    "veo":veo(action,at),"grok":grok(action,at,cam)}

beats=[
 # HOOK (come-to-life from ref) + PREVIEW (skill scripting style: hook -> what's coming -> breakdown -> outro)
 {"id":"hook","at":"scene","sentence":"Every one of these candles has a defect right now, and I can fix each one in about thirty seconds, without ever melting it down and starting over.","hook":True,
  "veo":veo("Starting from the reference image, the same woman stands at her workshop table behind a row of finished candles, a few visibly flawed; she glances over them and gives a small confident nod. Small natural motion only.","scene"),
  "grok":grok("The same woman stands at her rustic workshop table behind a row of candles, a few visibly flawed, and gives a small confident nod as she looks them over.","scene","Slow gentle push-in")},
 B("prev1","Here is what is coming up: a leaning wick, a sinkhole, a rough top, a tunnel, loose toppings, a long wick, wet spots, and a crooked label.",
   "Slow pan across a rustic wooden table lined with eight finished cream candles in glass jars, each with a small different flaw, a heat gun, scissors and a wick bar beside them.","scene","Slow tracking pan left to right"),
 B("prev2","No repouring, no waste, just quick little fixes. So grab your heat gun and let us save these candles.",
   "Close-up of a hand picking up a small handheld heat gun from the rustic wooden table among the candles.","scene","Static close shot, slight push-in"),

 # FIX 1 — off-center wick -> recenter
 B("f1a","Defect one: the wood wick set leaning hard against the side of the glass.",
   "Extreme close-up of a set cream candle in a clear glass jar with a flat wooden wick frozen leaning against the side of the jar.","defect","Static macro shot"),
 B("f1b","Warm the top with a heat gun for a few seconds, then nudge the wick back to the centre with a wick bar.",
   "Close-up of a heat gun warming the surface of a cream candle, then a metal wick bar gently sliding the softened wooden wick back to the centre of the jar.","center","Handheld close follow"),
 B("f1c","Hold it ten seconds while it sets, and it stands perfectly straight again.",
   "Close-up of a wick bar resting across the jar rim holding the wooden wick centred and upright in the cooling wax.","center","Static close shot"),

 # FIX 2 — sinkhole -> heat gun remelt
 B("f2a","Defect two: a deep sinkhole that opened up around the wick as it cooled.",
   "Top-down close-up of a set cream candle with a deep crater and sinkhole around the central wick.","defect","Static top-down"),
 B("f2b","Just melt the top smooth with the heat gun. The surface liquefies and flows level, filling the hole.",
   "Close-up of a heat gun pointed down at a cream candle top, the surface melting into a smooth level pool that fills the sinkhole.","heatgun","Slow push-in, handheld"),
 B("f2c","Let it re-set and the top is flawless, no second pour needed.",
   "Close-up of a smooth flawless re-set cream candle top in a clear glass jar held to the window light.","result","Static close, slow tilt"),

 # FIX 3 — rough/bumpy top -> smooth finish
 B("f3a","Defect three: a rough, bumpy, dull-looking top.",
   "Extreme close-up of a cream candle with a lumpy uneven matte surface.","defect","Static macro"),
 B("f3b","One slow pass with the heat gun melts just the surface into a glassy smooth finish.",
   "Close-up of a heat gun sweeping slowly across a cream candle top, the surface turning smooth and glossy.","heatgun","Handheld slow pan"),

 # FIX 4 — tunneling -> heat gun the ring
 B("f4a","Defect four: tunneling, where the wax burned straight down leaving a hard ring around the edge.",
   "Top-down close-up of a burned cream candle that has tunneled down the middle, a thick wall of unmelted wax around the rim.","defect","Static top-down"),
 B("f4b","Warm that ring with the heat gun until it melts down level with the middle.",
   "Close-up of a heat gun melting the raised wax ring of a tunneled candle until the whole surface is level.","heatgun","Slow push-in"),
 B("f4c","Now the next burn will reach the full width of the jar.",
   "Close-up of an even, fully level cream candle surface in a clear glass jar.","result","Static close"),

 # FIX 5 — loose toppings -> secure
 B("f5a","Defect five: dried botanicals on top that are loose and falling off.",
   "Close-up of a cream candle topped with loose dried lavender and flower petals, a few pieces sliding off the edge.","defect","Static close"),
 B("f5b","A quick burst of heat gun melts the surface just enough to set the botanicals firmly into the wax.",
   "Close-up of a heat gun briefly warming the top of a botanical-topped candle, then a finger gently pressing the dried lavender into the softened wax so it stays embedded.","toppings","Handheld close"),

 # FIX 6 — long sooty wick -> trim
 B("f6a","Defect six: a long wick burning with a big, smoky, sooty flame.",
   "Close-up of a cream candle burning with an oversized smoky flame and a thin trail of black soot.","defect","Static close"),
 B("f6b","Blow it out, let it cool, and trim the wick to a quarter inch with scissors.",
   "Extreme close-up of small scissors closing on a single upright wick and snipping the charred tip clean off, the trimmed piece falling away, the wick still standing.","trim","Macro, static"),
 B("f6c","Relight it and the flame is small, calm and clean.",
   "Close-up of a freshly trimmed cream candle burning with a small neat steady flame.","result","Static close"),

 # FIX 7 — wet spots -> heat gun the glass
 B("f7a","Defect seven: wet spots, those cloudy patches where the wax pulled away from the glass.",
   "Extreme close-up of a cream candle in a clear glass jar showing cloudy wet-looking patches against the glass wall.","defect","Static macro"),
 B("f7b","Warm the outside of the glass with the heat gun and the wax softens and re-sticks, clearing the spots.",
   "Close-up of a heat gun warming the outside of a clear glass candle jar, the cloudy patches clearing as the wax re-adheres to the glass.","heatgun","Slow orbit, handheld"),

 # FIX 8 — crooked label -> reposition
 B("f8a","And defect eight: a label stuck on crooked.",
   "Close-up of a cream candle jar with a plain kraft label applied crooked and lifting at one corner.","defect","Static close"),
 B("f8b","Peel it gently, line it up, and smooth it back down straight.",
   "Close-up of fingers peeling a plain kraft label off a glass jar and smoothing it back on perfectly straight and level.","label","Handheld close"),

 # OUTRO (skill style)
 B("out1","Eight defects, eight quick fixes, and not a single candle melted down and repoured.",
   "Slow wide pan across the rustic table now lined with eight flawless finished candles in glass jars, warm window light.","result","Slow tracking pan"),
 B("out2","Save this for your next batch, tell me which defect you battle most, and happy candle making.",
   "Warm close-up of a single finished cream candle burning gently in a clear glass jar on the workshop table, shelves softly behind.","result","Static close, slow push-in"),
]

VOICE={"provider":"elevenlabs","voiceId":"5u41aNhyCU6hXOcjPPv0","modelId":"eleven_multilingual_v2","speed":1.12}

def write(engine, model, clip_len, promptkey, folder):
    bdir=os.path.join(folder,"Project files"); os.makedirs(bdir,exist_ok=True)
    os.makedirs(os.path.join(folder,"Source clips"),exist_ok=True)
    mbeats=[]
    for b in beats:
        mb={"id":b["id"],"type":"broll","sentence":b["sentence"],"prompt":b[promptkey]}
        mbeats.append(mb)
    M={"title":"Candle Defects You Can Fix WITHOUT Repouring - In 30 Seconds Each ("+engine+")",
       "channel":"Candice's Country Candles","narrator_voice":VOICE,"aspect":"16:9",
       "video_model":model,"clip_len":clip_len,"reference_photo_url":REF,
       "continuity_bible":WORLD,"beats":mbeats}
    json.dump(M,open(os.path.join(bdir,"manifest.json"),"w"),indent=2)
    return len(mbeats)

n1=write("VEO","veo-video",8.0,"veo",os.path.join(ROOT,"..","video2_veo"))
n2=write("GROK","grok-imagine-video",6.0,"grok",os.path.join(ROOT,"..","video2_grok"))
print(f"wrote veo manifest ({n1} beats) and grok manifest ({n2} beats)")
print("sample veo f2b:", beats[8]["veo"][:160])
print("sample grok f2b:", beats[8]["grok"][:160])
