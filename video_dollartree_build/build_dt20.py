#!/usr/bin/env python3
"""I Tried EVERY Dollar-Tree Candle (20-minute deep dive) — image-visuals format.
~38% talking head, the rest full-frame images / split-screen / come-to-life / hands B-roll.
Uses the upgraded engine (iPhone realism, consistent bench, 1:1 splits, per-seg loudnorm,
fixed br() arg order). Writes video_dt20_veo/Project files/manifest.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import imgkit as K
B=[]; n=[0]
def _id(tag): i=n[0]; n[0]+=1; return f"b{i:03d}_{tag}"
def th(s, scene="bench", moved=False):
    B.append({"id":_id("th"),"type":"character","visual_mode":"talking_head","sentence":s,
              "seed":K.SCENES[scene],"prompt":K.th_prompt(s,scene,moved)})
def full(subject, narration, shot="close-up", kb="in"):
    B.append({"id":_id("full"),"type":"image","visual_mode":"image_full","sentence":narration,
              "image_prompt":K.image_prompt(subject,shot),"kenburns":{"dir":kb},"narration":narration})
def split(sentence, subject, scene="bench", th_side="left", shot="close-up"):
    B.append({"id":_id("split"),"type":"image","visual_mode":"image_split","sentence":sentence,
              "seed":K.SCENES[scene],"prompt":K.th_prompt(sentence,scene),"image_prompt":K.image_prompt(subject,shot),
              "ar":"1:1","split":{"th_side":th_side,"th_frac":0.46}})
def live(subject, motion, narration, shot="macro"):
    B.append({"id":_id("live"),"type":"image","visual_mode":"image_live","sentence":narration,
              "image_prompt":K.image_prompt(subject,shot),"motion":motion,"narration":narration})
NO_MAKING=(" She is NOT making candles: no pouring wax, no melting, no stirring, no pitcher, no thermometer, no wax. "
"The candles are FINISHED store-bought jar candles.")
def br(action, narration):
    pr=(f"Close-up POV iPhone shot of ONLY the hands and forearms of a mid-fifties woman (fair naturally-aged skin, "
    f"plain wedding band, blue sweater cuffs, tan apron) as she {action}.{NO_MAKING} Her hands ONLY — absolutely NO "
    f"face, NO head, NO other person. {K.PHONE} {K.NOTEXT} Setting: {K.WS}")
    B.append({"id":_id("br"),"type":"broll","visual_mode":"broll","narration":narration,"prompt":pr,"broll_ref":K.HANDS})

# ============================ ACT 1 — HOOK ============================
th("Okay, I did something a little bit unhinged. I drove to the Dollar Tree and I bought every single candle in the store.")
full("an overhead flat-lay of dozens of cheap dollar-store candles — glass jars, votives, tea lights and little tins — spread across a rustic wooden bench","Every jar, every votive, every tea light, every weird little tin. If it had a wick, it came home with me.","overhead")
live("a single cheap glass jar candle lit with a small warm flame in a dim cozy workshop","the flame flickers and dances and a thin wisp of smoke curls up","Then I lit all of them, one by one, because I needed to know — can a candle that costs one dollar actually be good?")
th("And the answer genuinely surprised me. Some were shockingly good. Some were honestly a little dangerous. And a few I would buy again tomorrow.")
full("a row of cheap candles where one burns beautifully with a clean flame and another has thick black soot climbing up the glass","By the end of this you will know exactly which ones are worth your dollar and which ones to leave on the shelf.","close-up")
th("So stick with me, because this is the most thorough dollar-store candle test you will ever watch.")

# ============================ ACT 2 — THE HAUL & METHOD ============================
th("Let me show you what a dollar actually buys you these days. Here is the whole haul.","shelf")
full("a wooden bench completely covered with cheap dollar-store candles of every kind, neatly arranged in rows","I ended up with around thirty different candles, and the whole haul cost me less than a single fancy candle would.","wide")
br("slides cheap glass jar candles into a neat row along the wooden bench, turning each one so its label faces the camera","First I lined every candle up and sorted them into groups, so the test would be fair.")
th("Because you cannot judge a tea light the same way you judge a big glass jar. So I split them into four categories.")
full("four small groups of candles on a bench — glass jars in one group, votives in another, tea lights in a third, and novelty tins in the fourth","Glass jars, votives, tea lights, and the novelty tins. Four categories, one identical test for each.","close-up")
th("And the test was simple. Same room, no drafts, same shelf, and I timed and watched every single burn.")
br("sets a small kitchen timer down on the bench next to a lit candle and presses the button","I gave each candle a full burn, I watched the melt pool, the flame, the smoke, and the smell.")
th("I was looking for four things. Does it burn evenly. Is the flame safe. Does it actually smell like anything. And is it worth the dollar.")
full("a simple handwritten-style checklist on a card next to a candle, with four boxes — but no readable words, just a card and a pen","Four questions, every candle, no exceptions. Let us start with the most important one — the burn.","close-up")

# ============================ ACT 3 — THE BURN TEST (JARS) ============================
th("So here is the real test. How does a one-dollar candle actually burn?","kitchen")
split("The first thing I look at is the melt pool. A good candle melts evenly, all the way out to the edge of the glass.","a top-down view of a lit candle with a full even pool of liquid wax reaching the edge of a clear glass jar","kitchen","left")
th("That full, even pool is the sign of a healthy candle. It means the whole top layer is melting like it should.")
live("a cheap candle burning with a tall flickering flame and a tunnel forming straight down the middle of the wax","the tall flame wavers and flickers and a faint trail of dark smoke lifts off the tip","But then I lit this one. Look at the flame. It is way too tall, it is dancing all over the place, and it is already tunneling.")
split("See that? It is burning straight down the middle and leaving a thick wall of wax all the way around the edge.","a clear glass jar candle with a deep narrow tunnel burned down the center and a thick ring of unmelted wax around the sides","kitchen","right")
full("a cross-section view of a tunneled candle showing how much hard wax is wasted around the outside","That ring of wax is wax you paid for and will never get to burn. On a cheap candle, that can be almost half the jar.","close-up")
th("Tunneling was by far the most common problem. More than half of the jars did it, and it is the fastest way to waste your money.")
br("points at the thin off-center wick of a finished jar candle, then at a candle with a thicker centered wick to compare","And almost every time, the reason was the wick. Too thin, or sitting off to one side.")
th("A thin, cheap wick cannot melt the full width of the jar, so it just bores a hole straight down. That is tunneling in one sentence.")
live("a cheap candle with thick black soot climbing up the inside of the glass jar","the flame flickers and more dark soot drifts upward and clings to the glass","And a handful of them did this. That black smoke is soot, and it is the wick burning dirty.")
full("a close-up of heavy black soot stains streaking up the inside of a candle jar glass","Soot is not just ugly. It is unburned carbon going into the air of your room, which is the last thing you want from a candle.","close-up")
br("holds a soot-stained candle jar up toward the bright window and slowly rotates it so the dark stains catch the light","When the glass looks like this after one burn, that candle is telling you something. It is not burning clean.")
th("So already, on the burn alone, the cheap jars split into two camps. The ones that melt clean, and the ones that tunnel and smoke.")

# ============================ ACT 4 — VOTIVES & TEA LIGHTS ============================
th("Now the little guys. The votives and the tea lights. These are where the dollar store really makes its money.","shelf")
full("a small pile of cheap votive candles and tea lights in their thin metal cups on a wooden bench","You get a whole bag of these for a dollar, so the value can be incredible — if they actually work.","close-up")
live("a single tea light burning in its thin metal cup, the wax already turning to liquid","the small flame flickers gently and the wax pool spreads across the little cup","Tea lights are honestly the most reliable thing in the whole store. Small wick, small wax, hard to get wrong.")
th("Because the cup is so small, the wax melts edge to edge almost instantly. No room to tunnel. That is why they just work.")
split("The votives were a different story. Half of them slumped over and drowned their own wick in melted wax.","a votive candle that has collapsed and flooded its own flame with a puddle of melted wax","window","left")
full("a votive candle burning unevenly with wax spilling over one side onto the bench","And a few votives leaked. The wax ran straight over the side because the candle was softer than it should be.","close-up")
th("So for the little candles, my rule is simple. Tea lights, yes. Loose votives, be careful.")

# ============================ ACT 5 — SCENT THROW ============================
th("Okay. The burn is one thing. But let us be honest, the entire point of a candle is the smell.","kitchen")
split("Cold, straight out of the jar, almost every single one of them smelled amazing. Strong, sweet, exactly like the label.","an extreme close-up of a person's nose and closed eyes leaning down to the rim of a candle jar, smelling it","window","right")
th("But cold smell is a trap. Anyone can make wax smell good when your nose is two inches away from it.")
th("The real test is the hot throw. Once it is lit, can you actually smell it from across the room?")
full("a single small lit candle on a coffee table in a large, mostly dark living room","So I put each one in a real room, lit it, sat down on the couch, and waited to see if the scent would travel.","wide")
live("a cozy living room slowly filling with warm candlelight, a single candle glowing on the table","the candle glow gently pulses and soft shadows shift across the room","And this is where most of them completely vanished. Lit, in a real room, I could barely smell a thing.")
th("It is the most common dollar-candle letdown. Smells incredible in the jar, smells like nothing once it is actually doing its job.")
split("But a few of them — maybe four or five — genuinely filled the whole room. And those are the real winners.","a warm glowing candle on a side table in a cozy room with soft light spreading outward","shelf","left")
th("Those are the candles that punch so far above one dollar it is almost unfair. We will get to my favorites in a minute.")
full("a simple comparison of two lit candles side by side, one in a bright open room and one in a dim room","Here is my honest rule. Cold smell tells you nothing. Hot throw tells you everything. Always judge a candle lit.","close-up")

# ============================ ACT 6 — SAFETY ============================
th("Now I need to get a little serious, because a couple of these genuinely worried me.","bench")
live("a cheap candle whose flame has grown far too large and aggressive, flickering wildly in a dim room","the oversized flame leaps and flickers violently and throws jumping shadows on the wall","This one. Watch the flame. It got huge, way bigger than a candle flame should ever be.")
split("A flame this tall in a thin glass jar is dangerous. The glass gets hot, and thin glass plus heat is how jars crack.","a candle with an alarmingly tall flame inside a thin glass jar, the glass looking hot and stressed","bench","right")
full("a candle jar that has cracked down the side with melted wax leaking out onto a wooden surface","And yes — one of mine actually cracked. The jar split, the wax ran out, and that could have been a real problem.","close-up")
th("So please, if you ever see a cheap candle burning with a giant flame like that, blow it out. No scent is worth a fire.")
br("pinches a too-long black wick on a finished candle and points at how long and curled it has grown","Most of the time, a giant flame just means the wick is way too long. And that is something you can actually fix.")
th("Which brings me to the single most useful candle tip I know, and almost nobody does it.")
split("Before you light any candle, trim the wick down to about a quarter inch. That one step fixes most of these problems.","a hand trimming a candle wick down short with small scissors, the trimmed wick tip falling away","bench","left")
full("a close-up comparison of a long untrimmed wick next to a neatly trimmed short wick on two candles","Long wick, big smoky flame. Short trimmed wick, small clean flame. It is the easiest upgrade you will ever make.","close-up")
th("I trimmed the wicks on the worst offenders and re-lit them, and honestly, several of them completely turned around.")
live("a cheap candle now burning with a small, calm, steady flame after the wick was trimmed","the small flame glows steadily and calmly with almost no flicker","Same candle, same dollar, just a trimmed wick. Look how calm that flame is now. Night and day.")

# ============================ ACT 7 — THE WINNERS ============================
th("Alright. The good news. Let me show you the candles that genuinely impressed me.","shelf")
full("a warm amber-colored dollar-store vanilla jar candle glowing beautifully on a shelf, looking surprisingly upscale","My number one was this simple vanilla jar. It burned clean, it threw scent across the whole room, and it looked great.","close-up")
split("Full even melt pool, no soot at all, and a scent that actually filled the room. For a dollar, that is incredible.","a top-down view of a clean clear glass candle with a perfect even melt pool and spotless glass","shelf","left")
th("If you only buy one candle on your next dollar-store run, make it a plain vanilla jar. That one earns its dollar twice over.")
full("a cozy dollar-store eucalyptus or fresh-linen scented candle glowing on a windowsill","My second favorite was a fresh linen one. Clean burn, and a light scent that did not give me a headache.","close-up")
live("a warm room at dusk lit only by a single glowing candle, gentle shadows swaying on the wall","the warm candlelight gently pulses and the shadows sway softly across the wall","When a one-dollar candle can light a room like this and smell good doing it, it is genuinely hard to complain.")
th("And the tea lights, as a group, were the best pure value in the whole store. Reliable, clean, and basically free.")
full("a cluster of lit tea lights glowing together warmly on a wooden bench","A handful of tea lights costs about a dollar and they all just work. For everyday use, nothing beats them.","close-up")
th("So those are the winners. A vanilla jar, a fresh linen jar, and a bag of honest little tea lights.")

# ============================ ACT 8 — THE LOSERS ============================
th("Now the part you came for. The ones to avoid.","bench")
full("a cheap candle with a deep ugly tunnel and a wall of wasted wax, looking sad and half-used","Any jar with a thin off-center wick. These are the tunnelers, and they waste half the wax you paid for.","close-up")
full("a candle jar with heavy black soot all up the glass after a single burn","Anything that sooted up the glass this badly after one burn. Dirty flame, dirty air, easy skip.","close-up")
split("And the heavily perfumed ones that smell overwhelming in the jar but give you a headache the second you light them.","a candle with an overpowering amount of fragrance, shown with exaggerated scent in a small room","window","right")
th("Those super strong artificial scents were almost always the weakest hot throw and the worst smell once they were actually burning.")
full("a novelty candle shaped or colored in a gimmicky way that looks fun but cheap","And honestly, most of the novelty candles. You are paying for the shape, not for the wax or the wick.")
th("So if it looks like a toy more than a candle, just know you are buying the look, not the burn.")

# ============================ ACT 9 — VALUE BREAKDOWN ============================
th("Let us talk actual value, because cheap is not the same as good value.","kitchen")
full("a simple visual of a candle next to a clock or timer, suggesting how many hours it burns","The real number that matters is cost per hour of burn. A dollar candle that lasts ten hours is ten cents an hour.","close-up")
th("And by that math, the good tea lights and the clean vanilla jar were some of the best value candles I have ever tested. Full stop.")
split("But a tunneling jar that wastes half its wax? You are really paying double, because you only get to burn half of it.","a half-wasted tunneled candle next to a fully-burned clean candle for comparison","bench","left")
full("a side-by-side of a fully used clean candle jar and a half-wasted tunneled jar","Same dollar, half the burn time. That is why a cheap candle that tunnels is not actually cheap at all.","close-up")
th("So when you judge value, do not look at the price. Look at how much of that wax you will actually get to use.")

# ============================ ACT 10 — PRO TIPS ============================
th("Before the final verdict, here are the tips that made the biggest difference in my testing.","shelf")
split("Tip one. Always trim the wick to a quarter inch before every single burn. This fixes flames, smoke and soot.","a hand trimming a candle wick neatly with scissors before lighting it","shelf","right")
th("Tip two. The very first burn matters most. Let the wax melt all the way to the edge before you blow it out.")
live("a candle on its first burn with the melt pool slowly spreading all the way to the glass edge","the melt pool slowly widens and the wax surface gleams as it reaches the edge","If you blow it out too early on the first burn, you train the candle to tunnel forever. Let that first pool reach the edge.")
br("cups a hand around a lit candle to shield it, showing how to keep it away from a draft","Tip three. Keep it away from drafts. A breeze makes the flame dance, and a dancing flame is what causes soot.")
th("Tip four. Stop burning it when there is about a half inch of wax left. Below that, the glass overheats and you risk a crack.")
full("a candle burned down to the last half inch of wax with the flame close to the bottom of the jar","Once you are down to the last little bit, the flame sits right against the glass. That is the danger zone. Just stop there.","close-up")
th("Four tiny habits. Trim, full first burn, no drafts, and know when to stop. They turn a cheap candle into a good one.")

# ============================ ACT 7b — NAMED JAR REVIEWS ============================
th("Now let me actually walk you through the jars one by one, because the differences were huge.","bench")
full("a warm vanilla bean scented dollar-store jar candle glowing on the bench","Candle one. Classic vanilla. Clean even burn, gentle scent, looked twice its price. An easy recommend.","close-up")
split("Candle two. A cinnamon spice jar. Smelled incredible cold, but the hot throw was weak and it sooted a little.","a cinnamon-and-spice colored jar candle with a faint trace of soot starting on the glass","bench","right")
full("a fresh-linen blue-tinted dollar-store jar candle burning cleanly on a windowsill","Candle three. Fresh linen. One of my favorites. Light, clean, no headache, and a genuinely even melt pool.","close-up")
live("a deep red apple-cinnamon jar candle burning with a slightly tall flame","the flame wavers tall and a little restless above the dark red wax","Candle four. Apple cinnamon. The flame ran hot and tall, and it needed a wick trim before it behaved.")
full("a green pine or eucalyptus scented dollar-store jar candle glowing softly","Candle five. Pine. Surprisingly natural smelling, burned clean, and it was perfect for a kitchen.","close-up")
split("Candle six. A heavy floral. This one was the headache candle. Way too much fragrance, and almost no hot throw.","an overpoweringly perfumed pink floral candle in a small room","window","left")
th("So even within the jars, you can see it. Simple scents and centered wicks win. Loud floral and thin wicks lose.")

# ============================ ACT 5c — SCENT FAMILIES ============================
th("Let me zoom out and talk about scent families, because there was a clear pattern.","kitchen")
full("a small group of bakery-scented candles — vanilla, sugar cookie, cinnamon roll — on the bench","The bakery scents, vanilla and sugar and cookie, were the most reliable. Warm, cozy, and they actually carried.","close-up")
full("a group of fresh and clean scented candles — linen, cotton, rain — on the bench","The fresh and clean scents were hit or miss. The good ones were lovely, the bad ones smelled like soap.","close-up")
split("The floral candles were the weakest as a group. Strong in the jar, gone in the room, and often a little fake.","a cluster of floral scented candles in soft light","shelf","right")
full("a group of woody and earthy scented candles — cedar, pine, sandalwood — on the bench","And the woody scents, cedar and pine, were the dark horse. The natural ones smelled genuinely expensive.","close-up")
th("So if you are shopping blind, my advice is simple. Reach for bakery and woody scents first, and be cautious with heavy florals.")

# ============================ ACT 6c — CONTAINERS & PLACEMENT ============================
th("Something nobody talks about with cheap candles is the container itself.","bench")
split("Thin glass is the enemy. The thinner the jar, the faster it heats up, and the more likely it is to crack.","a close-up comparing a thin flimsy glass candle jar with a thicker sturdier one","bench","left")
full("a candle in a thin glass jar sitting directly on a wooden surface with heat marks forming","Always put a cheap candle on a plate or a coaster, never straight onto wood or plastic. The base gets hotter than you think.","close-up")
br("slides a small plate under a lit candle jar to protect the wooden bench underneath","One little saucer under the jar, and you never have to worry about a heat ring or a crack on your furniture.")
th("And never put a cheap candle near anything that can catch — curtains, paper, a stack of napkins. The flames on these are unpredictable.")
full("a candle placed safely in the center of a clear table away from any clutter","Give it space, give it a hard surface, and keep an eye on it. Cheap candles need a little more babysitting.","close-up")

# ============================ ACT 8b — MORE LOSERS & MYTHS ============================
th("Let me bust a couple of dollar-candle myths while we are here.","shelf")
th("Myth one. A stronger smell in the jar means a stronger candle. Completely false. The loudest jars were almost always the weakest once lit.")
split("Myth two. More wax means it lasts longer. Also false. A big jar that tunnels gives you less burn than a small one that melts evenly.","a big tunneled candle next to a small fully-melting candle showing which lasts longer","kitchen","right")
th("Myth three. Color tells you the scent. Nope. Half of these were dyed a color that had nothing to do with how they smelled.")
full("several candles in colors that clearly do not match their scent labels lined up on a bench","Do not trust the color. Trust the wick, trust a sniff, and trust the burn. That is the whole game.","close-up")
th("And the single worst candle in the whole test? A novelty one that barely lit, smelled like plastic, and tunneled in ten minutes.")
full("a sad gimmicky novelty candle that has barely burned and looks cheap","You are paying for the gimmick, not the candle. Skip the cute ones and buy the boring ones. The boring ones work.","close-up")

# ============================ ACT 10c — RESCUING A BAD CANDLE ============================
th("Now here is the fun part. Even a bad dollar candle can usually be saved. Let me show you three rescues.","bench")
split("Rescue one. The tunnel fix. If your candle has tunneled, wrap foil around the top into a little dome and relight it.","a candle with a ring of aluminum foil shaped into a dome over the top of the jar","bench","left")
live("a tunneled candle with a foil dome over it, the trapped heat slowly melting the wall of wax back down","the wax around the edge slowly softens and melts down flatter under the trapped heat","The foil traps the heat, melts down that wasted wall of wax, and resets the surface flat. It honestly works like magic.")
full("a candle that has been rescued, now showing a flat even wax surface after the foil treatment","Twenty minutes under foil, and a tunneled candle comes back to a flat, even, full melt pool. Free fix.","close-up")
th("Rescue two. The flame is too small and weak? The wick is probably drowning in wax. Pour a little of that liquid wax off.")
br("carefully tips a lit candle to pour a little excess melted wax off into a small dish, freeing the wick","Pour off just a little of the pooled wax so the wick can stand tall again, and the flame comes right back to life.")
th("Rescue three. A candle that smells like nothing? Burn it in the smallest room you have, like a bathroom, and suddenly it is plenty.")
full("a small candle filling a tiny cozy bathroom with warm light and scent","A weak hot throw in a big living room is a great hot throw in a small room. Match the candle to the space.","close-up")
th("So before you toss a disappointing candle, try one of those three. Most of the time, you can bring it back.")

# ============================ ACT 9b — STORE COMPARISON ============================
th("People always ask me, is the Dollar Tree actually better or worse than the other cheap stores?","shelf")
full("candles from a few different discount stores lined up together for comparison on the bench","So I grabbed a few from other discount stores too, and burned them the exact same way to compare.","wide")
split("Honestly? The quality was all over the place everywhere. A dollar candle is a dollar candle, no matter the logo on the door.","two similar cheap candles from different stores burning side by side","kitchen","right")
th("The brand on the shelf mattered way less than the wick in the jar. A good wick beat a fancy label every single time.")
full("a close-up of two candles where the cheaper-looking one clearly has the better centered wick","So do not pay extra for the store name. Pick up the jar, look at the wick, and let that decide for you.","close-up")
th("That one habit — checking the wick before you buy — will save you more money than shopping at any particular store.")

# ============================ ACT 11 — FINAL VERDICT ============================
th("So here is my honest final verdict after burning every single candle in the store.","window")
full("a final overview shot of all the tested candles grouped into a good pile, a mediocre pile, and a bad pile","About a third were genuinely good. A third were okay. And a third I would never light again.","wide")
th("A one-in-three hit rate sounds rough. But once you know what to look for, you can spot the good third before you even buy.")
split("Look for a thick, centered wick. Give it a quick sniff. And lean toward simple scents over the loud artificial ones.","a close-up of a well-made candle with a thick centered wick, the clear sign of a good cheap candle","bench","left")
th("Do that, and a dollar-store candle run stops being a gamble and starts being one of the best deals in the whole store.")
full("a warm hero shot of the winning vanilla candle glowing beautifully, the champion of the test","And if you only remember one thing — the simple vanilla jar was the champion. Clean burn, real scent, one dollar.","close-up")

# ============================ ACT 12 — CTA ============================
th("If this saved you from a few bad candles and a wasted afternoon, do me a favor and subscribe, because I test stuff like this every week.")
th("And tell me down in the comments — what is the best cheap candle you have ever stumbled on? I am genuinely always hunting for the next one.")

M={"title":"I Tried EVERY Dollar-Tree Candle (20 Minute Deep Dive)","channel":"Candice's Country Candles","beats":B}
folder=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","video_dt20_veo")
json.dump(M,open(os.path.join(folder,"Project files","manifest.json"),"w"),indent=2)
from collections import Counter
c=Counter(b["visual_mode"] for b in B)
print(f"{M['title']}\n  {len(B)} beats | mix: {dict(c)}")
print(f"  TH share: {(c['talking_head'])/len(B)*100:.0f}%")
# rough runtime estimate: TH/split ~8s, full ~ (words/2.7+0.6)s, live ~ same, broll ~ same
def est(b):
    vm=b["visual_mode"]
    if vm in("talking_head","image_split"): return 8.0
    w=len(b.get("narration","").split()); return max(3.0, w/2.7+0.6)
secs=sum(est(b) for b in B)
print(f"  est runtime: {secs/60:.1f} min ({secs:.0f}s)")
