#!/usr/bin/env python3
"""Video 4 (Veo only) — "Candle Defects You Can Fix WITHOUT Repouring — In 30
Seconds Each", FULL ~10 min, HYPER-SPECIFIC choreographed prompts.
Rules baked in:
- Every B-roll prompt is an ordered micro-choreography (inventory -> sequence ->
  resolution) with object sizes/materials and ENUMERATED labels.
- B-roll shows ONLY hands/process/candles (never the character mouthing words).
- Talking heads speak on-camera (VO silenced during them by the assembler).
- Hook = the character coming to life and speaking (keyframe = reference)."""
import json, os
ROOT=os.path.dirname(os.path.abspath(__file__))
REF=open("/tmp/raw_ref.txt").read().strip()

WORLD=("A cozy rustic home candle workshop: a reclaimed-wood worktable; wooden shelves behind "
"lined with amber fragrance bottles and rows of finished cream candles in clear straight-sided "
"glass jars; a bright window with soft natural daylight; a black handheld heat gun, black wick "
"trimmer scissors, a stainless steel wick-centering bar, natural wood wicks, cotton wicks, twine "
"and dried lavender on the table.")
LINEUP=("On the table, five finished cream soy candles in identical clear straight-sided glass jars "
"stand in a row; each wears a small kraft paper label, two short words in clean serif, left to "
"right: 'LAVENDER & SAGE', 'VANILLA BEAN', 'COZY HEARTH', 'AMBER & SPRUCE', 'SUNDAY MORNING'. No "
"other text anywhere in the frame.")
IPHONE=("Filmed casually on a modern smartphone, wide ~26mm lens, deep focus, natural window "
"daylight, slight handheld micro-shake, true-to-life color; no bokeh, no film grain, no grade.")
PERSON=("The woman, when visible, is the exact same person as the reference image: mid-fifties, "
"tortoiseshell glasses, curly grey hair, blue knit sweater, tan canvas apron; identical every shot.")
HANDS=("Only the woman's weathered hands and forearms (blue sweater sleeves, tan apron) are in "
"frame doing the work — her face is NOT shown and she is NOT speaking in this shot.")
GLOBAL=("Object permanence: every object present at the first frame stays present and consistent; "
"nothing appears, multiplies, or vanishes; shelf items stay put; the apron and sweater are already "
"on from frame one; hands have exactly five fingers and hold tools correctly.")
SCENE={
 "trim":"A single wick is clearly present and upright before the cut; the scissor blades close ON the wick and cut at the stated height; the severed piece drops as described; the remaining wick stays rooted. Never cut empty air or wax.",
 "center":"A real wick is present; the centering tool actually contacts and holds THAT wick; the wick is visible the whole time. Never a tool holding nothing.",
 "heatgun":"The black heat gun nozzle is held a few inches above the wax and points down at the surface; the surface visibly melts and flows as described; the tool is real and present throughout. No floating tool, no instant jump.",
 "toppings":"The dried botanicals are real and present on the wax; they are pressed/melted in and stay embedded. Nothing floats, multiplies, or vanishes.",
 "label":"A real kraft label is peeled and repositioned continuously by the fingers; it is never teleported; its short text stays the same.",
 "defect":"A still, honest look at the flaw; nothing is being changed yet; everything physically stable.",
 "result":"A clean finished candle, physically stable; nothing changing, appearing, or vanishing.",
 "scene":"Everything physically stable and continuous; nothing appears or disappears.",
}
NEG=("NEGATIVE: no cutting empty air, no missing wick, no tool holding nothing, no floating tools, "
"no liquid through a closed lid, nothing spawning or vanishing, no clothing snapping on, no extra "
"or fused fingers, no warped faces, no gibberish or warped text, no label words other than those named.")

def broll(action, at):
    return f"{action} {HANDS} {SCENE[at]} {IPHONE} {PERSON} Scene world: {WORLD} GLOBAL: {GLOBAL} {NEG}"
def th(action, line):
    return (f"{action} She looks straight at the camera and speaks warmly, clearly and a little "
    f"earnestly in a natural American accent, lips fully in sync, saying exactly: \"{line}\". "
    f"{IPHONE} {PERSON} Scene world: {WORLD} GLOBAL: {GLOBAL} {NEG}")

def B(id,sent,action,at): return {"id":id,"type":"broll","sentence":sent,"prompt":broll(action,at)}
def C(id,line,action,kf=False):
    d={"id":id,"type":"character","sentence":line,"prompt":th(action,line)}
    if kf: d["hook"]=True
    return d

beats=[
 # HOOK — character comes to life, speaks (keyframe = reference); VO silent
 C("hook","Before you melt down another so-called ruined candle and pour the whole thing again, watch this, because I can fix every one of these defects in about thirty seconds.",
   "Starting from the reference image, the same woman stands behind her workshop table with a small row of finished candles in front of her, leaning in slightly toward the camera with a warm, knowing smile.", kf=True),
 # PREVIEW (b-roll, VO) — enumerate the lineup
 B("prev1","I lined up five of my own candles, and every single one has a different little flaw that I see makers panic over.",
   f"A slow handheld pan from left to right along the row of five candles. {LINEUP} The pan reveals each jar in turn, all sitting still on the wood table.","defect"),
 B("prev2","A leaning wick, a sinkhole, a rough top, a stubborn tunnel, and loose toppings. Not one of them needs repouring.",
   "A slow pan continues across the same five candles; the first has a wood wick tilted to one side, the second a cratered sunken top, the third a lumpy uneven surface, the fourth a deep tunnel down the middle, the fifth loose dried lavender scattered on top.","defect"),
 B("prev3","All I am going to use is a heat gun, a pair of wick scissors, and a little wick bar. So grab yours and let us rescue them.",
   "Close-up of the woman's hand picking up a black handheld heat gun from the wood table; beside it on the table lie black wick-trimmer scissors and a stainless steel wick-centering bar.","scene"),

 # FIX 1 — off-center wood wick
 B("f1a","Defect one, the leaning wick. This wood wick set hard against the side of the glass, which makes a candle burn down lopsided.",
   "Extreme close-up of the 'LAVENDER & SAGE' candle: a single flat 8 mm-wide natural wood wick is frozen leaning against the right inner wall of the clear glass jar, set into smooth cream wax.","defect"),
 B("f1b","I warm just the top layer with the heat gun for about ten seconds until the surface turns glossy and soft.",
   "Close-up: the woman's hand holds the black heat gun nozzle about three inches above the 'LAVENDER & SAGE' candle and sweeps it slowly; the top quarter-inch of cream wax turns wet and glossy while the wood wick stays standing.","heatgun"),
 B("f1c","Then I slide the wick gently back to dead centre with the steel wick bar and hold it for a few seconds.",
   "Close-up: the woman's fingers lower a stainless steel wick-centering bar across the jar rim; its slot catches the leaning wood wick and slides it left to the exact centre of the softened wax, then holds it upright and still.","center"),
 B("f1d","As the wax re-hardens the wick stays perfectly straight, and that candle is saved.",
   "Close-up of the 'LAVENDER & SAGE' candle now with its flat wood wick standing perfectly upright and centred in a smooth, re-set cream surface.","result"),

 # FIX 2 — sinkhole
 B("f2a","Defect two, the sinkhole. As this one cooled it shrank and cracked open a deep crater right around the wick.",
   "Top-down close-up of the 'VANILLA BEAN' candle: a deep funnel-shaped sinkhole has opened in the cream wax around the central cotton wick, leaving a cracked pit.","defect"),
 B("f2b","Instead of repouring, I just melt the top smooth with the heat gun. The surface liquefies and flows level, filling the hole on its own.",
   "Close-up: the woman's hand holds the heat gun a few inches over the 'VANILLA BEAN' candle; the cream surface melts into a shallow liquid pool that flows inward and fills the sinkhole until the top is flat and glassy.","heatgun"),
 B("f2c","Let it sit two minutes and the top sets perfectly flat, with no second pour and no wasted wax.",
   "Close-up of the 'VANILLA BEAN' candle with a completely flat, glossy, re-set cream top in the clear glass jar, held briefly toward the window light.","result"),

 # TALKING HEAD 1
 C("th1","Now this next one is the defect I get asked about more than any other, so pay attention.",
   "The woman stands behind the row of candles, resting one hand on the table, smiling warmly at the camera."),

 # FIX 3 — rough top
 B("f3a","Defect three, the rough top. This one set lumpy, matte and uneven, the kind of finish that looks homemade in a bad way.",
   "Extreme close-up of the 'COZY HEARTH' candle: the cream wax surface is bumpy, cratered and matte, uneven across the whole top of the clear glass jar.","defect"),
 B("f3b","One slow pass with the heat gun melts only the surface, and surface tension pulls it into a flat, glassy, professional finish.",
   "Close-up: the woman's hand sweeps the heat gun slowly across the 'COZY HEARTH' candle top; the lumpy matte surface melts and smooths into a flat, glossy, mirror-like cream finish.","heatgun"),

 # FIX 4 — tunneling
 B("f4a","Defect four, tunneling. This candle burned straight down the middle and left a thick wall of hard wax around the edge.",
   "Top-down close-up of the 'AMBER & SPRUCE' candle: a narrow burned tunnel runs down the centre around the wick, with a thick ring of unmelted cream wax left standing around the rim.","defect"),
 B("f4b","I warm that whole ring with the heat gun until the raised wax melts down and flows level with the middle.",
   "Close-up: the woman's hand moves the heat gun in slow circles over the raised outer ring of the 'AMBER & SPRUCE' candle; the thick wax wall melts and flows inward until the entire surface is one level pool.","heatgun"),
 B("f4c","Now the next burn reaches the full width of the jar instead of digging another tunnel.",
   "Close-up of the 'AMBER & SPRUCE' candle with a flat, even, fully level cream surface edge to edge in the clear glass jar.","result"),

 # FIX 5 — loose toppings
 B("f5a","Defect five, loose toppings. The dried lavender on this one never stuck, so it sheds petals everywhere.",
   "Close-up of the 'SUNDAY MORNING' candle: dried lavender buds and small flower petals sit loose on the cream surface, a few sliding off the edge onto the table.","defect"),
 B("f5b","A short burst of heat gun melts just the surface, then I press the botanicals down with my fingertip so they set into the wax.",
   "Close-up: the woman's hand gives the 'SUNDAY MORNING' top a brief heat-gun pass until the surface glistens, then a single fingertip gently presses each dried lavender bud down into the softened cream wax so it stays embedded.","toppings"),

 # TALKING HEAD 2
 C("th2","See how none of that needed a fresh pour? Every fix uses heat you already have on the bench.",
   "The woman holds up one finished candle toward the camera and smiles, the row of candles on the table in front of her."),

 # FIX 6 — long sooty wick
 B("f6a","Defect six, the long wick. This cotton wick is far too long, so it burns with a big smoky flame and leaves black soot on the glass.",
   "Close-up of a lit cream candle: a tall cotton wick burns with an oversized, flickering, smoky orange flame, and a faint black soot mark is forming on the inside of the clear glass.","defect"),
 B("f6b","Blow it out, let it cool, then trim the wick to a quarter inch with the scissors. The blades close on the wick and the burnt tip drops away.",
   "Extreme close-up: the woman's hand holds black wick scissors; the open blades close on the upright cotton wick about a quarter inch above the wax; the blackened one-centimetre tip is severed and drops straight down onto the table to the right; the short trimmed wick stays standing.","trim"),
 B("f6c","Relight it and the flame is small, steady and clean, and the candle will burn for hours longer.",
   "Close-up of the freshly trimmed cream candle relit with a small, calm, steady teardrop flame and no smoke.","result"),

 # FIX 7 — wet spots
 B("f7a","Defect seven, wet spots. These cloudy patches are where the wax shrank and pulled away from the glass as it cooled.",
   "Extreme close-up of a cream candle in a clear glass jar with several cloudy, wet-looking patches where the wax has separated from the inside of the glass wall.","defect"),
 B("f7b","I warm the outside of the glass with the heat gun, the wax softens against it and re-sticks, and the cloudy patches disappear.",
   "Close-up: the woman's hand moves the heat gun slowly around the outside of the clear glass jar; the cloudy wet patches clear from the bottom up as the cream wax softens and re-adheres to the glass.","heatgun"),

 # TALKING HEAD 3
 C("th3","A few more quick ones, and then I will show you the one mistake that actually is worth a repour.",
   "The woman stands at the table, hand resting beside the candles, smiling at the camera."),

 # FIX 8 — frosting
 B("f8a","Defect eight, frosting. That white crystal bloom on the surface is natural in soy, but it can look dusty.",
   "Extreme close-up of a cream soy candle surface covered in a fine white frosty crystal bloom across the top of the clear glass jar.","defect"),
 B("f8b","A single light heat-gun pass melts the very top skin and the frosting melts away to a smooth, even cream colour.",
   "Close-up: the woman's hand gives one light, quick heat-gun pass across the frosted cream surface; the white bloom melts away leaving a smooth, even, glossy cream top.","heatgun"),

 # FIX 9 — crooked label
 B("f9a","Defect nine, a crooked label. This kraft label went on tilted and is lifting at one corner.",
   "Close-up of a cream candle jar whose small kraft 'COZY HEARTH' label is stuck on visibly tilted, with the top-right corner peeling up away from the glass.","defect"),
 B("f9b","I peel it back gently, line it up level with the rim, and smooth it down from the centre out so there are no bubbles.",
   "Close-up: the woman's fingers slowly peel the tilted 'COZY HEARTH' kraft label off the glass, reposition it straight and level with the jar rim, and smooth it flat from the centre outward; the same two words stay on the label.","label"),

 # FIX 10 — mushroom wick
 B("f10a","Defect ten, the mushroom. After burning, this wick built a little black ball of carbon on the tip.",
   "Extreme close-up of a cooled cream candle: the cotton wick has a small round black carbon 'mushroom' bulb on its tip.","defect"),
 B("f10b","I pinch the black mushroom off and trim the wick clean with the scissors so the next burn stays bright.",
   "Extreme close-up: the woman's hand brings black scissors to the wick and snips off the round black carbon bulb plus a few millimetres of wick; the small black bead drops onto the table and the clean short wick stays upright.","trim"),

 # TALKING HEAD 4 / CTA
 C("th4","So before you ever start a candle over from scratch, reach for the heat gun first. Tell me in the comments which defect you fight the most.",
   "The woman leans in slightly toward the camera, both hands resting on the table beside the row of now-flawless candles, smiling warmly."),

 # OUTRO (b-roll)
 B("out1","Ten defects, ten quick fixes, and not one candle melted down and repoured. That is real money and real wax saved.",
   f"A slow wide handheld pan across the row of five candles, now all flawless with flat glossy tops and straight wicks. {LINEUP}","result"),
 B("out2","Save this for your next batch, and happy candle making. I will see you back here at the table.",
   "Warm close-up of one finished cream candle burning gently with a small steady flame in a clear glass jar on the wood table, shelves softly behind.","result"),
]

VOICE={"provider":"elevenlabs","voiceId":"5u41aNhyCU6hXOcjPPv0","modelId":"eleven_multilingual_v2","speed":1.1}
folder=os.path.join(ROOT,"..","video4_veo")
os.makedirs(os.path.join(folder,"Project files"),exist_ok=True)
os.makedirs(os.path.join(folder,"Source clips"),exist_ok=True)
M={"title":"Candle Defects You Can Fix WITHOUT Repouring - In 30 Seconds Each",
   "channel":"Candice's Country Candles","narrator_voice":VOICE,"aspect":"16:9",
   "video_model":"veo-video","clip_len":8.0,"reference_photo_url":REF,
   "continuity_bible":WORLD,"beats":beats}
json.dump(M,open(os.path.join(folder,"Project files","manifest.json"),"w"),indent=2)
nb=sum(1 for b in beats if b["type"]=="broll"); nc=sum(1 for b in beats if b["type"]=="character")
print(f"video4 manifest: {len(beats)} beats ({nb} broll, {nc} talking heads incl hook)")
