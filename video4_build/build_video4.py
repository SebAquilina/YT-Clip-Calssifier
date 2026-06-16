#!/usr/bin/env python3
"""Video 4 (Veo only) — "Candle Defects You Can Fix WITHOUT Repouring — In 30
Seconds Each", FULL ~10 min, HYPER-SPECIFIC choreographed prompts, LABEL-FREE
(Veo garbles label text), strict character-visibility, talking-head hook."""
import json, os
ROOT=os.path.dirname(os.path.abspath(__file__))
REF=open("/tmp/raw_ref.txt").read().strip()

WORLD=("A cozy rustic home candle workshop: a reclaimed-wood worktable; wooden shelves behind "
"lined with amber fragrance bottles and rows of finished plain cream candles in clear straight-"
"sided glass jars; a bright window with soft natural daylight; a black handheld heat gun, black "
"wick-trimmer scissors, a stainless steel wick-centering bar, natural flat wood wicks, cotton "
"wicks, twine and dried lavender on the table. All candles are PLAIN and UNLABELED — clean cream "
"wax in clear glass, no labels, no writing, no text anywhere in the frame.")
IPHONE=("Filmed casually on a modern smartphone, wide ~26mm lens, deep focus, natural window "
"daylight only, slight handheld micro-shake, true-to-life color; no bokeh, no film grain, no "
"color grade, no studio lighting, no glow or rim-light.")
PERSON=("The woman, when visible, is the exact same person as the reference image: mid-fifties, "
"tortoiseshell glasses, curly grey hair, blue knit sweater, tan canvas apron; identical every shot.")
HANDS=("ONLY the woman's weathered hands and forearms (blue sweater sleeves, tan apron) are in "
"frame doing the work — her face is NOT shown and she is NOT speaking in this shot.")
GLOBAL=("Object permanence: every object present at the first frame stays present and consistent; "
"nothing appears, multiplies or vanishes; shelf items stay put; the apron and sweater are already "
"on from frame one; hands have exactly five fingers and hold tools correctly.")
SCENE={
 "trim":"A single wick is clearly present and upright before the cut; the scissor blades close ON the wick at the stated height and cut it; the severed piece drops as described; the remaining wick stays rooted. Never cut empty air or wax.",
 "center":"A real wick is present; the centering tool actually contacts and holds THAT wick, which stays visible the whole time. Never a tool holding nothing.",
 "heatgun":"The black heat-gun nozzle is held a few inches above the wax pointing down; the surface visibly melts and flows as described; the tool is real and present throughout. No floating tool, no instant jump.",
 "toppings":"The dried botanicals are real and present on the wax; they are pressed/melted in and stay embedded. Nothing floats, multiplies or vanishes.",
 "label":"plain unlabeled jar; no text appears.",
 "defect":"A still, honest look at the flaw; nothing is being changed yet; everything physically stable.",
 "result":"A clean finished plain candle, physically stable; nothing changing, appearing or vanishing.",
 "scene":"Everything physically stable and continuous; nothing appears or disappears.",
}
NEG=("NEGATIVE: no cutting empty air, no missing wick, no tool holding nothing, no floating tools, "
"no liquid through a closed lid, nothing spawning or vanishing, no clothing snapping on, no extra "
"or fused fingers, no warped faces, no labels, no writing, no text or numbers anywhere.")

def broll(action,at): return f"{action} {HANDS} {SCENE[at]} {IPHONE} {PERSON} Scene world: {WORLD} GLOBAL: {GLOBAL} {NEG}"
def th(action,line): return (f"{action} She looks straight at the camera and speaks warmly, clearly "
    f"and a little earnestly in a natural American accent, lips fully in sync, saying exactly: "
    f"\"{line}\". {IPHONE} {PERSON} Scene world: {WORLD} GLOBAL: {GLOBAL} {NEG}")
def B(i,s,a,at): return {"id":i,"type":"broll","sentence":s,"prompt":broll(a,at)}
def C(i,line,a,kf=False):
    d={"id":i,"type":"character","sentence":line,"prompt":th(a,line)}
    if kf: d["hook"]=True
    return d

# helper to make a 3-4 beat fix compactly
beats=[]
def add(*bs): beats.extend(bs)

# ---- HOOK + INTRO ----
add(
 C("hook","Before you melt down another so-called ruined candle and pour the whole thing again, stop, because I can fix nearly every candle defect in about thirty seconds without repouring a single one.",
   "Starting from the reference image, the same woman stands behind her workshop table with a small row of plain cream candles in front of her, leaning in slightly toward the camera with a warm, knowing smile, lit only by soft window light.", kf=True),
 B("i1","I have been pouring candles for fifteen years, and the biggest waste of wax I see is makers tossing a perfectly fixable candle in the bin.",
   "A slow handheld pan across a rustic wood table holding several plain unlabeled cream candles in clear glass jars, a black heat gun, black scissors and a steel wick bar laid beside them.","scene"),
 B("i2","Every flaw you are about to see, I used to think meant starting over, and every one of them I now fix in seconds with tools already on my bench.",
   "Close-up of the woman's hand slowly moving along the row of plain cream candles, lightly touching the rim of each clear glass jar in turn.","defect"),
 C("th_intro","So grab a heat gun, a pair of wick scissors and a wick bar, and let me show you.",
   "The woman holds up a small black handheld heat gun toward the camera with a friendly smile, the row of plain candles on the table in front of her."),
)

# ---- FIX FACTORY ----
def fix(n, defect_s, defect_a, action_s, action_a, action_at, detail_s, detail_a, detail_at, result_s, result_a):
    p=f"f{n}"
    add(
     B(p+"a", defect_s, defect_a, "defect"),
     B(p+"b", action_s, action_a, action_at),
     B(p+"c", detail_s, detail_a, detail_at),
     B(p+"d", result_s, result_a, "result"),
    )

fix(1,
 "Defect one, the leaning wick. This flat wood wick set hard against the side of the glass, so the candle would burn down completely lopsided.",
 "Extreme close-up of a plain cream candle in a clear glass jar: a single flat eight-millimetre natural wood wick is frozen leaning against the right inner wall, set in smooth cream wax.",
 "I warm just the top layer with the heat gun for about ten seconds, until the surface turns wet and glossy and the wax around the wick softens.",
 "Close-up: the woman's hand holds the black heat-gun nozzle three inches above the candle and sweeps slowly; the top quarter-inch of cream wax turns wet and glossy while the wood wick stays standing.","heatgun",
 "Then I drop the steel wick bar across the rim, catch the wick in its slot, and slide it back to dead centre.",
 "Close-up: the woman's fingers lower a stainless steel wick-centering bar across the jar rim; its slot catches the leaning wood wick and slides it left to the exact centre of the softened wax, holding it upright.","center",
 "Hold it ten seconds while it sets, and the wick stands perfectly straight, good as new.",
 "Close-up of the plain cream candle with its flat wood wick now standing perfectly upright and centred in a smooth re-set surface.")

fix(2,
 "Defect two, the sinkhole. As this one cooled it shrank and cracked open a deep crater right around the wick.",
 "Top-down close-up of a plain cream candle: a deep funnel-shaped sinkhole has opened in the wax around the central cotton wick, leaving a cracked pit.",
 "No repour needed. I melt the top smooth with the heat gun and the liquefied surface flows level and fills the hole on its own.",
 "Close-up: the woman's hand holds the heat gun a few inches over the candle; the cream surface melts into a shallow pool that flows inward and fills the sinkhole until the top is flat and glassy.","heatgun",
 "The trick is to keep the gun moving so you only melt the top few millimetres, not the whole candle.",
 "Close-up: the woman's hand keeps the heat gun moving in slow circles just above the melting cream surface, the thin liquid layer glossy and level.","heatgun",
 "Two minutes to set, and the top is flat and flawless with zero wasted wax.",
 "Close-up of the candle with a completely flat, glossy re-set cream top, held briefly toward the window light.")

fix(3,
 "Defect three, the rough top. This one set lumpy and matte, the kind of finish that screams amateur on a shelf.",
 "Extreme close-up of a plain cream candle whose wax surface is bumpy, cratered and matte across the whole top of the clear glass jar.",
 "One slow pass with the heat gun melts only the surface, and surface tension pulls it flat into a glassy, professional finish.",
 "Close-up: the woman's hand sweeps the heat gun slowly across the lumpy cream top; the matte bumpy surface melts and smooths into a flat, glossy, mirror-like finish.","heatgun",
 "If a stubborn lump remains, hold the heat on that spot alone for a second longer and it levels out.",
 "Close-up: the heat-gun nozzle pauses over one raised lump on the cream surface; the lump melts down flush with the rest of the glossy top.","heatgun",
 "Smooth, glossy, and it took about fifteen seconds.",
 "Close-up of the now flawless glossy cream candle top in the clear glass jar.")

add(C("th_a","This next one is the defect people give up on the most, and it is honestly the easiest to fix.",
   "The woman stands behind the row of plain candles, resting one hand on the table, smiling warmly at the camera."))

fix(4,
 "Defect four, tunneling. This candle burned straight down the middle and left a thick wall of hard wax around the edge.",
 "Top-down close-up of a plain cream candle with a narrow burned tunnel down the centre around the wick and a thick ring of unmelted cream wax standing around the rim.",
 "I warm that whole ring with the heat gun until the raised wax melts and flows inward, level with the middle.",
 "Close-up: the woman's hand moves the heat gun in slow circles over the raised outer ring; the thick wax wall melts and flows inward until the entire surface is one level pool.","heatgun",
 "Tunneling is just an uneven burn, and melting the ring resets the whole surface flat.",
 "Close-up: the last of the raised cream ring melts down into a single smooth level pool across the jar.","heatgun",
 "Now the next burn reaches the full width of the jar instead of digging another tunnel.",
 "Close-up of the candle with a flat, even cream surface edge to edge in the clear glass jar.")

fix(5,
 "Defect five, loose toppings. The dried lavender on this one never stuck, so it sheds petals everywhere.",
 "Close-up of a plain cream candle with dried lavender buds and small petals sitting loose on the surface, a few sliding off the edge onto the table.",
 "A short burst of heat gun melts just the surface, then I press each botanical down with a fingertip so it sets into the wax.",
 "Close-up: the woman's hand gives the top a brief heat-gun pass until it glistens, then a single fingertip gently presses each dried lavender bud down into the softened cream wax so it stays embedded.","toppings",
 "Press, do not bury. You want the lavender sitting in the surface, not drowned under it.",
 "Extreme close-up: a fingertip seats a dried lavender sprig just into the glossy cream surface so it sits flush and holds.","toppings",
 "Now the toppings are locked in and the candle is gift-shop ready.",
 "Close-up of the cream candle with dried lavender now firmly embedded and even across the surface.")

add(C("th_b","See the pattern? Almost everything is just heat, used in the right spot for the right number of seconds.",
   "The woman holds up one finished plain candle toward the camera and smiles, the row of candles on the table in front of her."))

fix(6,
 "Defect six, the long wick. This cotton wick is far too long, so it burns with a big smoky flame and blackens the glass.",
 "Close-up of a lit plain cream candle: a tall cotton wick burns with an oversized flickering smoky orange flame and a faint black soot mark forming on the inside of the clear glass.",
 "Blow it out, let it cool, then close the scissors on the wick a quarter inch above the wax. The blades cut, and the burnt tip drops away.",
 "Extreme close-up: the woman's hand holds black wick scissors; the open blades close on the upright cotton wick a quarter inch above the wax; the blackened one-centimetre tip is severed and drops straight down onto the table to the right; the short wick stays standing.","trim",
 "A quarter inch is the magic number, long enough to light, short enough to burn clean.",
 "Extreme close-up of the freshly trimmed short cotton wick standing upright and clean in the cream wax, the cut tip lying on the table beside the jar.","result",
 "Relight it and the flame is small, steady and clean, and the candle burns for hours longer.",
 "Close-up of the candle relit with a small, calm, steady teardrop flame and no smoke.")

fix(7,
 "Defect seven, wet spots. Those cloudy patches are where the wax shrank and pulled away from the glass as it cooled.",
 "Extreme close-up of a plain cream candle with several cloudy wet-looking patches where the wax has separated from the inside of the clear glass wall.",
 "I warm the outside of the glass with the heat gun. The wax softens against it, re-sticks, and the cloudy patches vanish.",
 "Close-up: the woman's hand moves the heat gun slowly around the outside of the clear glass jar; the cloudy wet patches clear from the bottom up as the cream wax softens and re-adheres to the glass.","heatgun",
 "Keep the gun a few inches off the glass and moving, so you warm it evenly without scorching.",
 "Close-up: the heat gun glides smoothly around the lower outside of the jar, the last cloudy patch clearing to reveal solid cream wax against clean glass.","heatgun",
 "Crystal clear glass, and it looks freshly poured again.",
 "Close-up of the candle with perfectly clear glass and smooth cream wax pressed against it, held to the window light.")

add(C("th_c","A few more quick ones, including the white dusty bloom that scares everybody, even though it is completely normal.",
   "The woman stands at the table, hand resting beside the plain candles, smiling at the camera."))

fix(8,
 "Defect eight, frosting. That white crystal bloom is natural in soy wax, but it can look dusty and old.",
 "Extreme close-up of a plain cream soy candle surface covered in a fine white frosty crystal bloom across the top of the clear glass jar.",
 "A single light pass with the heat gun melts the very top skin, and the white bloom melts away to smooth even cream.",
 "Close-up: the woman's hand gives one light quick heat-gun pass across the frosted surface; the white bloom melts away leaving a smooth, even, glossy cream top.","heatgun",
 "Do not overdo it, just kiss the surface with heat, because frosting is only skin deep.",
 "Close-up: the heat gun makes one final gentle pass and lifts away, leaving a clean glossy cream surface.","heatgun",
 "Even, smooth and rich looking again, no repour required.",
 "Close-up of the smooth even cream candle top with the frosting gone.")

fix(9,
 "Defect nine, the mushroom. After burning, this wick built a little black ball of carbon on the tip.",
 "Extreme close-up of a cooled plain cream candle: the cotton wick has a small round black carbon mushroom bulb on its tip.",
 "I close the scissors just under the black bulb and snip. The carbon ball drops away and the clean wick is left short and upright.",
 "Extreme close-up: the woman's hand brings black scissors to the wick and snips just below the round black carbon bulb; the small black bead drops onto the table and the clean short wick stays upright.","trim",
 "Mushrooming just means a little extra carbon, and trimming it keeps the next burn bright and smoke-free.",
 "Extreme close-up of the trimmed clean cotton wick standing upright, the black carbon bead resting on the wood table beside the jar.","result",
 "Clean wick, clean burn, thirty seconds.",
 "Close-up of the plain cream candle with a neat trimmed wick ready to relight.")

add(C("th_d","Now this one looks scary, but it is just the surface, and the surface is always fixable.",
   "The woman leans slightly toward the camera, hand on the table beside the candles, smiling."))

fix(10,
 "Defect ten, surface cracks. This top cooled too fast and crazed into a web of fine cracks.",
 "Extreme close-up of a plain cream candle top covered in a web of fine surface cracks across the wax in the clear glass jar.",
 "One slow heat-gun pass melts the cracked skin back together into a single smooth sheet of wax.",
 "Close-up: the woman's hand sweeps the heat gun slowly across the crazed cream surface; the fine cracks melt and flow together into one smooth glossy sheet.","heatgun",
 "Cracks come from cooling too fast, and gentle heat simply re-flows the top so they disappear.",
 "Close-up: the last cracks on the cream surface melt closed under the moving heat gun, leaving a flawless glossy top.","heatgun",
 "Smooth as glass again, and nobody would ever know.",
 "Close-up of the flawless smooth cream candle top in the clear glass jar.")

# ---- RECAP + CTA + OUTRO ----
add(
 C("th_cta","Ten defects, ten thirty-second fixes, and not one candle melted down and started over. So before you ever repour, reach for the heat gun first. Tell me in the comments which defect you fight the most.",
   "The woman leans in toward the camera, both hands resting on the table beside the row of now-flawless plain cream candles, smiling warmly."),
 B("out1","Every fix you just saw saved a whole candle, and over a year that is pounds of wax and real money kept in your pocket.",
   "A slow wide handheld pan across the row of plain cream candles, now all flawless with flat glossy tops and straight wicks, on the rustic wood table in soft window light.","result"),
 B("out2","Save this video for your next batch night, and happy candle making. I will see you back here at the table.",
   "Warm close-up of one plain cream candle burning gently with a small steady flame in a clear glass jar on the wood table, shelves softly behind.","result"),
)

VOICE={"provider":"elevenlabs","voiceId":"5u41aNhyCU6hXOcjPPv0","modelId":"eleven_multilingual_v2","speed":1.08}
folder=os.path.join(ROOT,"..","video4_veo"); os.makedirs(os.path.join(folder,"Project files"),exist_ok=True); os.makedirs(os.path.join(folder,"Source clips"),exist_ok=True)
M={"title":"Candle Defects You Can Fix WITHOUT Repouring - In 30 Seconds Each",
   "channel":"Candice's Country Candles","narrator_voice":VOICE,"aspect":"16:9",
   "video_model":"veo-video","clip_len":8.0,"reference_photo_url":REF,"continuity_bible":WORLD,"beats":beats}
json.dump(M,open(os.path.join(folder,"Project files","manifest.json"),"w"),indent=2)
nb=sum(1 for b in beats if b["type"]=="broll"); nc=sum(1 for b in beats if b["type"]=="character")
print(f"video4 manifest: {len(beats)} beats ({nb} broll, {nc} talking heads incl hook)")
