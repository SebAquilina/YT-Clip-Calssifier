#!/usr/bin/env python3
"""I Tried Every Dollar-Tree Candle - Here's What I Found.
Image-visuals format (references/image-visuals.md): ~35% talking head, the rest carried by
full-frame images, split-screen, come-to-life images and hands B-roll. Builds the manifest."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import imgkit as K
B=[]; n=[0]
def _id(tag): i=n[0]; n[0]+=1; return f"b{i:02d}_{tag}"
def th(s, scene="bench", moved=False):
    B.append({"id":_id("th"),"type":"character","visual_mode":"talking_head","sentence":s,
              "seed":K.SCENES[scene],"prompt":K.th_prompt(s,scene,moved)})
def img_full(subject, narration, shot="close-up", kb="in"):
    B.append({"id":_id("full"),"type":"image","visual_mode":"image_full","sentence":narration,
              "image_prompt":K.image_prompt(subject,shot),"kenburns":{"dir":kb},"narration":narration})
def img_split(sentence, subject, scene="bench", th_side="left", shot="close-up"):
    # split image pane is near-square -> generate at 1:1 so it is not warped when placed beside the TH crop
    B.append({"id":_id("split"),"type":"image","visual_mode":"image_split","sentence":sentence,
              "seed":K.SCENES[scene],"prompt":K.th_prompt(sentence,scene),"image_prompt":K.image_prompt(subject,shot),
              "ar":"1:1","split":{"th_side":th_side,"th_frac":0.46}})
def img_live(subject, motion, narration, shot="macro"):
    B.append({"id":_id("live"),"type":"image","visual_mode":"image_live","sentence":narration,
              "image_prompt":K.image_prompt(subject,shot),"motion":motion,"narration":narration})
# NOTE: br(action, narration) — first arg is the HAND ACTION (goes into the veo prompt), second is the
# SPOKEN narration (goes to TTS). Do NOT swap these: a swap makes the TTS read the stage direction aloud.
NO_MAKING=(" She is NOT making candles: no pouring wax, no melting, no stirring, no pitcher, no thermometer, no wax. "
"The candles are FINISHED store-bought jar candles.")
def br(action, narration):
    pr=(f"Close-up POV iPhone shot of ONLY the hands and forearms of a mid-fifties woman (fair naturally-aged skin, "
    f"plain wedding band, blue sweater cuffs, tan apron) as she {action}.{NO_MAKING} Her hands ONLY — absolutely NO "
    f"face, NO head, NO other person. {K.PHONE} {K.NOTEXT} Setting: {K.WS}")
    assert len(narration.split())>=4 and not narration.endswith(("-out","label-out")), f"br narration looks like a stage direction: {narration!r}"
    B.append({"id":_id("br"),"type":"broll","visual_mode":"broll","narration":narration,"prompt":pr,"broll_ref":K.HANDS})

# ===== HOOK =====
th("Okay, I did something a little ridiculous. I went to the Dollar Tree and I bought every single candle they had.")
img_full("an overhead flat-lay of a dozen cheap dollar-store glass jar candles and votives spread across a rustic wooden bench, plain inexpensive packaging","Every candle on the shelf, the jars, the votives, the little tins, all of it, for about a dollar each.","overhead")
img_live("a single cheap jar candle lit with a small warm flame in a cozy dim workshop, soft background","the flame flickers and dances, a thin wisp of smoke curls up","And I burned all of them, because I really wanted to know — can a one-dollar candle actually be good?")
th("Some of them genuinely surprised me, a couple were honestly a little scary, and one of them I would actually buy again.")
img_full("a row of cheap candles where one is clearly burning beautifully and another has thick black soot up the glass","Stick around, because by the end I will tell you the exact one that is worth your dollar, and the ones to skip.","close-up")

# ===== THE HAUL / METHOD =====
th("So here is what I did. I lined every candle up on my bench and gave each one a fair, identical test.")
br("lines up a row of cheap glass jar candles neatly on the wooden bench, turning each one label-out","I burned each one the same way, same room, no drafts, and I watched what actually happened.")
img_full("a close-up of a cheap candle label showing a generic fragrance name and a tiny printed warning, slightly blurry print","First thing I checked was the label, because a dollar candle still has to tell you what is inside.","close-up")
th("And right away you can see the difference between these and a proper candle. The wax is soft, the wicks are thin, and the fragrance is a mystery.")

# ===== BURN TEST =====
th("Now the real test. How does a dollar candle actually burn? This is where most of them either pass or completely fall apart.","kitchen")
img_split("Watch the melt pool. A good candle melts evenly all the way to the edge of the glass.","a close-up of a candle with a full even melt pool reaching the edge of the glass, warm glow","kitchen","left")
img_live("a cheap candle burning with a tall flickering flame and a tunnel forming down the middle, dim moody light","the tall flame wavers and flickers, a faint trail of black smoke lifts off the tip","But watch this one. The flame is way too tall, it is flickering, and it is already tunneling straight down the middle.")
img_full("a cheap jar candle with a deep tunnel burned down the center leaving a thick ring of unmelted wax around the edge","That tunnel means you are going to lose almost half the wax you paid for. It just gets left behind on the sides.","close-up")
th("Tunneling was the single most common problem. More than half of them did it, and it is the fastest way to waste a cheap candle.")
img_full("a close-up of black soot streaks climbing up the inside of a candle jar glass","And a few of them did this — sooty black smoke crawling right up the glass. That is the wick burning dirty.","close-up")
br("holds a sooty candle jar up to the window and slowly turns it, dark smoke stains visible on the glass","Soot like this is not just ugly, it means the candle is not burning cleanly in your room.")

# ===== SCENT THROW =====
th("Okay, but the whole point of a candle is the smell. So how is the scent throw on a one-dollar candle?")
img_split("a person's nose near a lit candle in a cozy living room, eyes closed, soft warm light","Cold, in the jar, almost all of them smelled amazing. Strong, sweet, exactly what the label promised.","window","right")
th("But cold smell is a trick. The real question is hot throw — can you actually smell it across the room once it is lit?")
img_full("a small lit candle on a coffee table in a large dim living room, the room mostly dark around it","And this is where most of them just disappeared. Lit, in a real room, I could barely smell a thing from the couch.")
th("A couple, though, genuinely filled the room. And those are the ones that punch way above their one-dollar price.")

# ===== THE GOOD ONES =====
th("So let me show you the winners, because there were some real ones.","shelf")
img_full("a warm amber-colored dollar-store jar candle glowing on a shelf, looking surprisingly nice and cozy","This vanilla one burned clean, threw scent across the whole room, and honestly looked more expensive than it was.","close-up")
img_split("This one had a full even melt pool, no soot, and a scent that actually filled the room. For a dollar, that is incredible.","a candle with a perfect clean even melt pool, no soot, glowing warmly","shelf","left")
img_live("a cozy room at dusk lit only by a warm glowing candle, gentle shadows on the wall","the warm candlelight gently pulses and the shadows sway softly on the wall","When a one-dollar candle does this, it is genuinely hard to argue with the value.")

# ===== THE BAD ONES =====
th("Now the ones to avoid. And please pay attention to this part, because a couple of these worried me.")
img_full("a cheap candle with a dangerously large flame and the glass jar looking very hot, slightly ominous lighting","This one's flame got huge and the jar got way too hot to touch. That is a real safety problem, not just a bad candle.","close-up")
img_live("a candle flame that is far too tall and aggressive, flickering wildly in a dark room","the oversized flame flickers violently and throws jumping shadows","A flame this size in a thin glass jar is exactly how cheap candles crack and fail.")
th("So if you ever see a dollar candle burning like that, blow it out. No scent is worth a cracked, overheating jar.")
img_full("a cracked candle jar with wax leaking onto a table surface","And yes, one of mine actually cracked. Lesson learned — never leave a cheap candle burning unattended.","close-up")

# ===== VALUE VERDICT =====
th("So here is the honest verdict after burning every single one of them.","window")
img_full("a simple side-by-side of one glowing nice candle next to one sooty tunneled candle on a bench","About a third were genuinely good, a third were mediocre, and a third I would never light again.","close-up")
th("For a dollar, a one-in-three hit rate is actually not bad — as long as you know what to look for before you buy.")
br("points at a candle wick, pinching it to show a thin poorly-made wick versus a thicker one","The trick is the wick. A thin, off-center wick is the number one sign a cheap candle is going to tunnel and smoke.")
th("Look for a wick that is centered and a decent thickness, give the jar a sniff, and you will dodge most of the bad ones.")

# ===== BEST PICK + CTA =====
th("And my single best pick? The simple vanilla jar. Clean burn, real scent throw, and it looked great on the shelf.","shelf")
img_full("a warm vanilla dollar-store candle glowing beautifully on a cozy shelf, the hero shot","If you only grab one candle on your next Dollar Tree run, make it a simple vanilla jar. That one earns its dollar.","close-up")
th("If this saved you a few wasted dollars and a couple of bad candles, subscribe, because I test stuff like this every single week.")
th("And tell me down in the comments — what is the best cheap candle you have ever found? I am genuinely always looking.")

M={"title":"I Tried Every Dollar-Tree Candle - Here's What I Found","channel":"Candice's Country Candles","beats":B}
folder=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","video_dollartree_veo")
json.dump(M,open(os.path.join(folder,"Project files","manifest.json"),"w"),indent=2)
from collections import Counter
c=Counter(b["visual_mode"] for b in B)
print(f"{M['title']}\n  {len(B)} beats | mix: {dict(c)}")
print(f"  TH share: {(c['talking_head'])/len(B)*100:.0f}%")
