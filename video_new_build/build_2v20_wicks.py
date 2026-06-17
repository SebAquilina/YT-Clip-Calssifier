#!/usr/bin/env python3
"""$2 Wicks vs $20 Wicks - Is The Expensive One Worth It? — FORMAT v5.3 via buildkit."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from buildkit import th, br, build

# ===== ACT 1 hook =====
th("So I bought the cheapest wicks I could find and the most expensive wicks I could find, and I burned them side by side to settle this once and for all.")
th("Two dollars versus twenty dollars. A ten times price difference for what is, honestly, a piece of braided cotton string. I had to know if it was worth it.")
th("Because the candle world is full of people telling you that you must buy the premium everything, and I am naturally a little suspicious of that.")
th("So I ran a real test. Same wax, same jars, same fragrance, same room. The only thing I changed was the wick. Cheap versus premium.")
br("A two dollar wick pack and a twenty dollar wick pack sitting side by side on the bench.","sets a cheap wick pack and a premium wick pack side by side on the bench and taps each one")
th("And the result genuinely surprised me, in both directions. So let me show you exactly what your money does and does not buy with candle wicks.")
# ===== ACT 2 what you're comparing =====
th("First, let me be fair about what these two things actually are, because it is not quite as simple as cheap versus good.")
th("The two dollar wicks were a big assorted bag, lots of sizes, almost no information, the kind you grab without thinking.")
th("The twenty dollar option was a documented, single-size pack from a proper candle supplier, tested in a specific wax, with a real spec sheet.")
br("The cheap assorted bag next to the neatly labeled premium box.","holds up the messy cheap bag in one hand and the labeled premium box in the other, comparing them")
th("So really, a lot of that price gap is not the cotton at all. It is the testing, the consistency, and the information that comes with it.")
th("Keep that in mind, because it changes the whole answer. You are not just paying for a nicer string. You are paying for knowing what the string does.")
# ===== ACT 3 the burn test =====
th("Okay, the test. I made identical candles, the only difference being the wick, and I did a proper timed burn on every single one.")
th("One hour of burn for every inch of jar diameter, watching the melt pool, the flame height, and how much soot each one threw.")
br("Two identical candles burning side by side, one wicked cheap and one wicked premium.","leans toward two identical candles burning side by side and points between the two flames")
th("The cheap wicks were a lottery. Some burned genuinely fine. Some tunneled badly. Some threw a tall, flickering, smoky flame from the very start.")
th("And the worst part was not that they were bad on average. It was that they were inconsistent. I could not predict which cheap wick would misbehave.")
th("The premium wicks, on the other hand, were boringly identical. Every single one gave me a clean, full, even melt pool and a calm, steady flame.")
th("That is the real thing you are buying at twenty dollars. Not magic. Just consistency. Every wick behaves like the last one.")
# ===== ACT 4 soot, flame, safety =====
th("Let me talk about soot and flame, because this is where the cheap ones actually worried me a little.")
th("A couple of the cheap wicks left black soot creeping up the inside of the glass, and the flame danced around like it could not settle.")
br("A jar with a smoky black ring of soot climbing the inside of the glass.","tilts a finished jar to show a dark smoky ring of soot climbing the inside of the glass")
th("Sooty, restless flames are not just ugly. They mean the wick is not matched to the wax, and it is burning fuel it cannot cleanly process.")
th("The premium wicks burned clean, with a steady teardrop flame and clear glass at the end. That is what a properly matched wick looks like.")
th("Now, to be fair, that is partly because the premium wick was correctly sized for my wax. A correctly sized cheap wick can also burn clean.")
th("But that is the whole point. With the premium pack I knew the size. With the cheap bag, getting a clean burn was pure luck.")
# ===== ACT 5 the cost-per-candle truth =====
th("Now let me do the math that actually matters, because the sticker price is genuinely misleading here.")
th("The two dollar bag had five hundred wicks. The twenty dollar pack had one hundred. So per wick, the cheap one is about half a cent, and the premium is twenty cents.")
br("A row of finished candles, a few marked as failures pulled to one side.","slides a few failed candles to one side of a row of finished candles, separating the good from the bad")
th("But here is the catch. With the cheap bag, a big chunk of those candles failed, and a failed candle wastes your wax, your fragrance, your jar, and your time.")
th("Your wax and fragrance and jar are worth far more than the wick. So a wick that ruins them is not cheap at all. It is the most expensive part of the whole candle.")
th("When I counted only the candles that actually came out sellable, the premium wick was basically the same cost per good candle, and sometimes cheaper.")
th("So the twenty dollar wick was not really ten times the price. Once you count the failures, it was about the same money for a far better result.")
# ===== ACT 6 when cheap is fine =====
th("Now, I do not want to be unfair to the cheap wicks, because there is absolutely a place for them.")
th("If you are just starting out and you are testing wick sizes to find your range, a cheap assorted pack is a perfectly reasonable way to experiment.")
br("A few different cheap wick sizes laid out in a row for testing.","lays out three different cheap wick sizes in a neat row on the bench for a test")
th("You are going to burn those test candles anyway, you are not selling them, so the inconsistency matters a lot less at that stage.")
th("The mistake is using a random cheap bag for the candles you actually care about, the ones you gift or sell. That is where it costs you.")
th("So my honest take is, test with cheap, produce with documented. Use the cheap pack to learn, then lock in a proper wick for the real thing.")
# ===== ACT 7 the verdict =====
th("So, is the expensive wick worth it? Here is my genuinely honest answer after burning all of these.")
th("You are not paying ten times more for better cotton. You are paying for consistency and for information, and for most makers, that is absolutely worth it.")
br("The premium box placed firmly in front of the cheap bag on the bench.","sets the premium wick box down firmly in front of the cheap bag, choosing it clearly")
th("Once you are making candles you care about, the premium documented wick saves you more in wasted wax and fragrance than it ever costs you up front.")
th("But if you are still finding your sizes, the cheap pack is a fine tool to learn with. Just do not build your real candles on a guess.")
# ===== ACT 8 CTA =====
th("So that is the two dollar versus twenty dollar wick test, and the answer is the one nobody likes. It depends, but mostly, yes, it is worth it.")
th("The cheap wick is for learning. The good wick is for producing. And the gap between them is consistency, which is the thing that actually makes candles repeatable.")
th("If this helped you spend your candle money smarter, subscribe, because I run real, honest tests like this one every single week.")
th("And tell me in the comments, are you team cheap or team premium right now, and I will tell you whether I think you should switch.")

build(title="$2 Wicks vs $20 Wicks - Is The Expensive One Worth It?", folder_name="video_2v20_veo")
