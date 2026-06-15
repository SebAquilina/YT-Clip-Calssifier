#!/usr/bin/env python3
"""Build the manifest for "I Fixed 100 DEFECTIVE Candles In A Row".
Comprehensive prompt system (the realism + consistency fix):
  every prompt = ACTION + iPhone-camera block + PERSON-consistency rule +
  verbatim WORLD bible + an explicit REALISM/anti-AI-tell negative clause."""
import json, os
ROOT=os.path.dirname(os.path.abspath(__file__))
REF=open("/tmp/ref_url.txt").read().strip()

WORLD=("A cozy home candle workshop in a converted farmhouse room: a large rustic "
"reclaimed-wood worktable; tall wooden shelves behind it lined with amber glass "
"fragrance bottles, blocks of pale soy wax, balls of natural twine and rows of "
"finished cream and amber candles in clear glass jars; a big bright window on the "
"right with soft natural daylight; a stainless steel pouring pitcher, a small "
"digital kitchen scale, scissors, cotton wicks and dried botanicals on the table. "
"Warm, homey, slightly rustic; palette of warm creams, honey amber, soft wood "
"browns and muted sage; bright natural daytime light, no artificial color grade.")

IPHONE=("Filmed casually on a modern smartphone held in one hand: wide ~26mm lens, "
"deep focus with the whole frame sharp, natural window daylight, slight handheld "
"micro-shake, true-to-life color and realistic fine detail; no bokeh, no shallow "
"depth of field, no film grain, no cinematic grade.")

PERSON=("Whenever a person appears she is the exact same woman as in the reference "
"image: a friendly woman in her mid-fifties, fair skin, round tortoiseshell "
"glasses, shoulder-length curly grey hair, a blue knit sweater over a tan canvas "
"apron; identical face, hair and clothing in every shot.")

REALISM=("Photo-real and physically correct: every object is solid, whole and clearly "
"present; any liquid pours from a real visible container into another real visible "
"container; hands have exactly five natural fingers and hold objects correctly; "
"tools actually contact and act on what they touch. NEGATIVE — do not show: "
"floating or disappearing objects, liquid appearing from nothing or poured into "
"empty air, bending or morphing tools, extra or fused fingers, warped or melting "
"faces, duplicated people, glowing outlines or rim-light around the person, and no "
"text, captions, watermarks, logos or gibberish labels anywhere.")

def P(action): return f"{action} {IPHONE} {PERSON} World: {WORLD} {REALISM}"
def PC(action,line): return (f"{action} She looks straight at the camera and speaks "
    f"warmly, clearly and a little earnestly with a slight Australian accent, her lips "
    f"fully and naturally in sync with the words, saying exactly: \"{line}\". "
    f"{IPHONE} {PERSON} World: {WORLD} {REALISM}")

def b(id,sent,act): return {"id":id,"type":"broll","sentence":sent,"prompt":P(act)}
def c(id,line,act): return {"id":id,"type":"character","sentence":line,"prompt":PC(act,line)}

beats=[
 # HOOK (generated separately from the clean thumbnail -> manual:True)
 {"id":"h00-hook","type":"broll","manual":True,
  "sentence":"Last month, one hundred candles came out of my workshop defective. Every single one.",
  "prompt":"(hook generated from the clean thumbnail keyframe)"},
 # INTRO
 b("b_int1","Sunken tops, frosted sides, and wicks drowning in the wax. A whole month of work, ruined.",
   "Slow handheld move across a rustic wooden workshop table crowded with flawed soy candles in clear glass jars: some with sunken cratered tops, some with pale frosted patches, one with a cotton wick collapsed sideways into the set wax."),
 b("b_int1b","I counted them twice. One hundred candles, and every one had something wrong with it.",
   "Close-up of a woman's hand moving along a long row of flawed candles on the wooden table, briefly touching the rim of one cratered candle after another."),
 c("c_int1","But instead of throwing them out, I decided to fix all one hundred.",
   "The woman stands behind her candle-covered worktable, gesturing gently over the flawed candles with both hands."),
 b("b_int2","Fixing a hundred mistakes in a row taught me more than ten years of getting it right.",
   "Close-up of the woman's hands lifting one flawed candle from the table and slowly turning it to inspect the sunken, cratered top."),
 c("c_int2","So here is every defect I found, and exactly how I fixed it.",
   "The woman looks warmly at the camera, both hands resting on the wooden table beside the candles."),
 # L1 wet spots -> warm jars
 b("l1a","The first defect was everywhere. Ugly wet-looking patches where the wax pulled away from the glass.",
   "Extreme close-up of a cream soy candle in a clear glass jar showing patchy wet-looking spots and pale frosting where the wax has separated from the glass wall."),
 b("l1b","The cause is cold glass, so now I warm every jar in the oven before I pour.",
   "Close-up of two hands in quilted oven mitts sliding a metal tray of clean empty clear glass jars into a warm home oven."),
 b("l1c","Warm glass and warm wax bond smoothly, and those spots vanish completely.",
   "Close-up of a smooth flawless cream candle in a clear glass jar held up to soft window light, the wax perfectly clear against the glass with no spots."),
 # L2 sinkholes -> pour temp + second pour
 b("l2a","The next defect was deep sinkholes that opened up around the wick as the candle cooled.",
   "Top-down close-up of a set cream candle with a deep crater and a sinkhole opening right around the single central cotton wick."),
 b("l2b","That happens when you pour too hot, so I let the wax cool to a hundred and thirty-five degrees first.",
   "Close-up of a hand holding a kitchen thermometer dipped into a stainless steel pitcher of melted cream wax, the dial showing a temperature."),
 b("l2c","Then a thin second pour fills the dip and leaves a flat, even top.",
   "Close-up of a thin stream of warm cream wax pouring from a stainless steel pitcher into the small dip on top of an already-set candle in a glass jar, filling it level."),
 b("l2d","Pouring slow and low is the whole secret to a glassy, level surface.",
   "Close-up of a slow gentle stream of cream wax filling a clear glass jar to a smooth flat surface on the wooden table."),
 # L3 ratios -> scale
 c("c_l3","This next one was quietly costing me whole batches.",
   "The woman holds up a small digital kitchen scale toward the camera with a knowing smile."),
 b("l3a","Half my candles had a weak, uneven scent because I was measuring the fragrance oil by eye.",
   "Close-up of a hand loosely glugging fragrance oil from an amber bottle straight into a pitcher of melted wax, a little spilling onto the wooden table."),
 b("l3b","A four-dollar kitchen scale fixed it. I weigh the wax, then weigh exactly ten percent oil.",
   "Close-up of an amber fragrance bottle drizzling oil into a glass jug of wax that sits on a lit digital kitchen scale, the display showing the weight."),
 b("l3c","Now every candle smells exactly the same, batch after batch.",
   "Slow close-up pan across a neat row of identical finished cream candles in clear glass jars on the wooden table."),
 # L4 crooked wicks -> clothespins
 b("l4a","So many candles set with the wick frozen leaning hard against one side of the glass.",
   "Close-up of a set cream candle in a clear glass jar with the single cotton wick frozen leaning against the side of the jar instead of centered."),
 b("l4b","The fix costs about a dollar. A wooden clothespin laid across the rim holds the wick dead centre.",
   "Close-up of a wooden clothespin resting across the rim of a glass jar, gently gripping a single cotton wick so it stands perfectly centered in the cooling cream wax."),
 b("l4c","I rest one on every jar, walk away, and they all set perfectly straight.",
   "Top-down close-up of a row of glass jars, each with a wooden clothespin laid across the top holding a centered cotton wick in setting cream wax."),
 b("l4d","No more crooked wicks ruining an otherwise perfect candle.",
   "Close-up of a finished cream candle in a glass jar with a single cotton wick standing perfectly upright and centered."),
 # L5 melt scraps
 c("c_l5","And the candles I truly could not save? I did not waste a single gram of them.",
   "The woman holds up a finished layered cream-and-amber candle in a glass jar toward the camera and smiles."),
 b("l5a","I scooped the wax out of every ruined candle and saved it in an old tin.",
   "Close-up of a metal spoon scooping set cream wax out of a flawed candle jar into an old metal tin already half full of broken wax scraps."),
 b("l5b","Melted back down, those scraps poured into brand-new layered candles, completely free.",
   "Close-up of warm melted wax pouring from a stainless steel pitcher into a clear glass jar, forming soft cream and amber layers."),
 b("l5c","Now those scrap candles are the ones my customers ask for by name.",
   "Close-up of a beautiful finished layered cream-and-amber candle standing on the rustic wooden table."),
 # L6 cure
 b("l6a","Some candles smelled wonderful cold but threw almost no scent once they were burning.",
   "Close-up of a lit cream candle with a small steady flame in a quiet room, only faint warmth rising above it."),
 b("l6b","The fix is patience. I cure every candle for two full weeks before it is allowed to burn.",
   "Slow close-up pan along a wooden shelf lined with rows of curing cream and amber candles in glass jars, a small handwritten paper date tag tucked beside one."),
 b("l6c","A cured candle throws twice the scent and fills the whole room.",
   "Warm close-up of a cream candle burning with a healthy flame on the wooden table, a cozy softly-lit room behind it."),
 # L7 sooty/tunnel -> trim wick
 b("l7a","A whole row burned with big smoky flames and tunneled straight down the middle.",
   "Close-up of a cream candle burning with an oversized flickering flame and a thin trail of black soot, the wax tunneling down a narrow hole around the wick."),
 b("l7b","The flame was too big because the wick was too long, so now I trim it before every burn.",
   "Extreme close-up of small scissors closing on a single upright black-tipped cotton wick and snipping the charred tip clean off, the trimmed piece falling away while the wick stays standing in the candle."),
 b("l7c","A quarter-inch wick gives a small, clean flame that burns for hours longer.",
   "Close-up of a freshly trimmed cream candle burning with a small neat steady flame in a clear glass jar."),
 # L8 oil quality
 b("l8a","Cheap fragrance was behind a lot of those weak-smelling batches too.",
   "Close-up of several tiny sample fragrance vials lined up on the wooden table beside one larger amber fragrance bottle."),
 b("l8b","One good oil in a four-ounce bottle costs far less per ounce and smells far better.",
   "Close-up of a hand choosing a larger four-ounce amber fragrance bottle from a wooden shelf lined with amber bottles."),
 # L9 reuse jars
 b("l9a","Every jar from a failed candle got a second life instead of the bin.",
   "Close-up of two hands washing an emptied clear glass candle jar in a sink of warm soapy water."),
 b("l9b","A soak in hot soapy water lifts the old wax and slides the paper label right off.",
   "Extreme close-up of fingers peeling a soaked paper label cleanly off a wet glass jar held under running water."),
 b("l9c","Last week's reject becomes this week's free, perfect container.",
   "Close-up of a row of sparkling clean empty glass jars standing upside down on a wooden drying rack by the bright window."),
 # L10 labels
 b("l10a","The last fix was the cheapest of all, and it doubled what people would pay.",
   "Close-up of a plain unlabeled cream candle in a clear glass jar sitting bare on the wooden table."),
 b("l10b","Plain kraft paper and a simple stamp turn a bare jar into something that looks boutique.",
   "Close-up of two hands pressing a rubber stamp onto a small brown kraft paper label, then smoothing the stamped label onto a cream candle jar."),
 b("l10c","A little twine and a sprig of dried lavender, and it belongs in a fancy shop.",
   "Close-up of hands tying natural twine and a small sprig of dried lavender around a kraft-labeled cream candle in a glass jar."),
 # RECAP / CTA / OUTRO
 c("c_recap","One hundred defective candles, and in the end not one of them was wasted.",
   "The woman stands proudly behind a wooden table now full of beautiful finished candles, smiling warmly at the camera."),
 b("b_recap","Ten little fixes turned a month of disasters into my best-selling batch ever.",
   "Slow wide handheld pan across the rustic wooden table covered in beautiful finished labeled candles, twine and dried botanicals, bright window light behind."),
 c("c_cta","Tell me in the comments which defect you have battled with. I read every single one.",
   "The woman leans in slightly toward the camera, smiling warmly with both hands resting on the wooden table beside the candles."),
 b("b_outro","Happy candle making, my friend. I will see you back here at the table.",
   "Warm close-up of a single finished cream candle burning gently in a clear glass jar on the rustic wooden workshop table, shelves of supplies softly visible behind."),
]

M={"title":"30. I Fixed 100 DEFECTIVE Candles In A Row - Here's What I Learned",
   "channel":"Candice's Country Candles",
   "narrator_voice":{"provider":"elevenlabs","voiceId":"5u41aNhyCU6hXOcjPPv0","modelId":"eleven_multilingual_v2"},
   "aspect":"16:9","video_model":"veo-video","reference_photo_url":REF,
   "continuity_bible":WORLD,"beats":beats}
json.dump(M,open(os.path.join(ROOT,"manifest.json"),"w"),indent=2)
nb=sum(1 for x in beats if x["type"]=="broll"); nc=sum(1 for x in beats if x["type"]=="character")
print(f"beats={len(beats)} broll={nb} character={nc} (hook manual)")
