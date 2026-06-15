#!/usr/bin/env python3
"""Build the expanded (~8 min) manifest, reusing existing clips.
Reused beat ids keep their downloaded clips in state.json; only NEW beats are
generated. All B-roll narration is re-TTS'd (sentences changed/lengthened)."""
import json, os, sys
ROOT=os.path.dirname(os.path.abspath(__file__))
REF=open("/tmp/ref_url.txt").read().strip()
BIBLE=("A cozy home candle workshop in a converted farmhouse room: a large rustic "
 "reclaimed-wood worktable, tall wooden shelves behind it lined with amber glass "
 "bottles of fragrance oil, stacked blocks of pale soy wax, balls of natural twine, "
 "and rows of finished cream and amber candles in glass jars; a big bright window on "
 "the right with soft natural daylight; a stainless steel pouring pitcher, a small "
 "kitchen scale, scissors, wicks and dried botanicals on the table. Warm, homey, "
 "slightly rustic. The maker is a friendly woman in her fifties with curly grey hair, "
 "glasses, and a blue knit sweater. Color palette warm creams, honey amber, soft wood "
 "browns, muted sage. Bright natural daytime light, no artificial color grade.")
IP=("Shot on a modern smartphone, deep focus everything sharp, wide lens, natural "
 "available light, slight handheld micro-shake, true-to-life color, crisp detail, "
 "no bokeh, no film grain, no on-screen text.")
def br(id,sent,vis): return {"id":id,"type":"broll","sentence":sent,"prompt":vis+" "+IP}
def ch(id,sent,vis): return {"id":id,"type":"character","sentence":sent,"prompt":vis+" "+IP}

beats=[
 # INTRO
 ch("b01-hook","These ten little candle hacks have saved me hundreds of dollars.",
    "Starting from the reference image, keep the woman, her blue knit sweater, glasses, curly grey hair and the candle workshop exactly as shown. Warm friendly smile, she gestures over the finished candles on the table."),
 br("n_intro_market","I sell these candles at the farmers market every single weekend.",
    "Close-up of hands arranging rows of finished cream and amber candles neatly into a rustic wooden market crate on the workshop table."),
 br("b02-intro","And honestly, you do not need fancy equipment or expensive supplies to make candles that people line up for.",
    "Slow close-up pan across a rustic wooden workshop table covered with candle-making supplies: amber fragrance bottles, blocks of pale soy wax, cotton wicks, a stainless steel pouring pitcher and rows of finished cream candles in glass jars."),
 br("n_intro_promise","But for years, I was quietly throwing money away on little mistakes that nobody ever warned me about.",
    "Close-up of a hand dropping a lumpy failed candle and a crumpled receipt into a small bin beside the wooden workshop table."),
 br("n_intro_tea","So pour yourself a cup of tea, and let me save you the money it took me a decade to figure out.",
    "Close-up of a warm cup of tea being set down on the rustic wooden table beside a few finished candles, steam rising softly."),
 # HACK 1 bulk wax
 br("b03-hack1","Hack one, and it is the big one. Buy your soy wax in bulk.",
    "Close-up of two hands lifting a large brown ten pound bag of pale soy wax flakes onto a rustic wooden table next to a tiny retail box of wax, comparison shot."),
 br("n_h1b","A little one pound box from the craft store can cost almost as much as a ten pound bag bought wholesale.",
    "Close-up of hands scooping pale soy wax flakes out of a big bulk bag into a glass measuring jug on the wooden table."),
 br("n_h1c","Making that one switch cut my wax bill by more than half, and it is the exact same wax.",
    "Close-up of a tall neat stack of pale soy wax blocks and a full bulk bag on the rustic wooden table."),
 # HACK 2 reuse jars
 br("b04-hack2","Hack two. Save and reuse your glass jars.",
    "Close-up of hands washing an empty glass candle jar in a sink of warm soapy water, then setting the clean clear jar upside down on a wooden drying rack among other reused jars."),
 br("n_h2b","A quick soak in hot soapy water lifts the old wax right out and the paper label slides off.",
    "Extreme close-up of fingers peeling a soaked paper label off a glass jar held under warm water."),
 br("n_h2c","Last week's empty candle becomes this week's free container, and your customers never know the difference.",
    "Close-up of a row of sparkling clean empty glass jars upside down on a wooden drying rack by the bright window."),
 ch("n_th_a","These first few hacks are the ones that saved me the most money.",
    "Starting from the reference image, keep the woman, her blue knit sweater, glasses, curly grey hair and the candle workshop exactly as shown. She looks warmly at the camera, one hand resting on the table beside the candles."),
 # HACK 3 scale
 br("b05-hack3","Hack three. A cheap kitchen scale beats measuring cups every time.",
    "Close-up of a small digital kitchen scale on a rustic wooden table with a glass measuring jug of pale soy wax flakes on it, a hand adding a few more flakes, the display lit."),
 br("n_h3b","When you weigh your wax and your oil, every single batch comes out the same.",
    "Close-up of a hand carefully pouring fragrance oil from an amber bottle onto a small digital scale holding a jug of wax, display showing the weight."),
 br("n_h3c","No more pulling a tray of candles out of the cupboard and finding half of them ruined.",
    "Close-up of a hand sliding out a tray of perfectly uniform finished cream candles in glass jars on the wooden table."),
 # HACK 4 clothespins
 br("b06-hack4","Hack four. Wooden clothespins hold your wicks perfectly straight while the wax sets.",
    "Close-up of a wooden clothespin resting across the rim of a glass jar, holding a single cotton wick centered and straight in cooling cream-colored wax."),
 br("n_h4b","A whole bag of them costs about a dollar and works better than the fancy wick holders they sell you.",
    "Close-up of a small pile of plain wooden clothespins on the rustic wooden table beside glass jars."),
 br("n_h4c","Just rest one across the top of each jar, walk away, and come back to a wick standing perfectly straight.",
    "Top-down close-up of several glass jars in a row, each with a wooden clothespin across the rim holding a centered wick in setting wax."),
 # HACK 5 scraps
 br("b07-hack5","Hack five. Do not throw away your wax scraps.",
    "Close-up of small leftover scraps of cream and amber candle wax being dropped into a stainless steel pouring pitcher on the wooden table."),
 br("n_h5b","Melt every leftover bit together and you get a beautiful layered candle for absolutely nothing.",
    "Close-up of warm melted wax being poured into a clear glass jar forming soft cream and amber layers on the rustic wooden table."),
 br("n_h5c","I keep an old tin just for scraps, and every few weeks it pays for a whole new batch.",
    "Close-up of an old metal tin on the wooden table filled with colorful broken candle wax scraps."),
 ch("b08-th1","I used to throw all of that away. Now my scrap candles are the ones my customers ask for by name.",
    "Starting from the reference image, keep the woman, her blue knit sweater, glasses, curly grey hair and the candle workshop exactly as shown. She holds up a finished layered candle in a glass jar toward the camera and smiles warmly."),
 # HACK 6 oil
 br("b09-hack6","Hack six. Buy your fragrance oil in four ounce bottles instead of tiny samples.",
    "Close-up of a hand placing a larger four ounce amber glass bottle of fragrance oil next to several tiny sample vials on the wooden table, rows of amber bottles on shelves behind."),
 br("n_h6b","The price per ounce drops like a stone, and a good oil is what makes a candle worth selling.",
    "Close-up pan along a wooden shelf lined with amber glass fragrance oil bottles, a hand reaching for a larger one."),
 br("n_h6c","Buying the size up feels expensive on the day, but it is the cheapest scent you will ever pour.",
    "Close-up of fragrance oil being poured from an amber bottle into a pitcher of melted wax, gentle swirl."),
 # HACK 7 warm jars
 br("b10-hack7","Hack seven. Warm your jars in the oven before you pour.",
    "Close-up of hands in oven mitts taking a tray of warm empty glass candle jars out of a home oven and setting them on the rustic wooden table ready for pouring."),
 br("n_h7b","It stops those ugly wet spots on the glass, so you are not remelting and redoing a whole batch.",
    "Extreme close-up of a smooth flawless freshly poured cream candle in a clear glass jar held up to the bright window light."),
 br("n_h7c","Warm glass and warm wax become friends, and the candle sets clear and smooth all the way down.",
    "Close-up of a clear glass jar of cream candle wax setting evenly and smoothly on the wooden table by the window."),
 ch("n_th_b","This next one took me years to learn, so please do not skip it.",
    "Starting from the reference image, keep the woman, her blue knit sweater, glasses, curly grey hair and the candle workshop exactly as shown. She leans in slightly toward the camera with a warm earnest smile."),
 # HACK 8 cure
 br("b11-hack8","Hack eight, and this is the secret one. Cure your candles for two full weeks before you burn them.",
    "Slow close-up pan across a wooden shelf lined with rows of finished cream and amber candles in glass jars curing, soft natural window light, dried botanicals beside them."),
 br("n_h8b","Curing just means letting the wax and the oil really bind together as they rest.",
    "Close-up of rows of candles resting on a wooden curing shelf, a small handwritten paper date tag tucked beside one jar."),
 br("n_h8c","A cured candle throws twice the scent, so you can use far less oil and still fill the whole room.",
    "Warm close-up of a single cream candle burning with a gentle flame in a glass jar on the wooden table, cozy softly-lit room behind."),
 # HACK 9 trim wick
 br("b12-hack9","Hack nine. Always trim your wick to a quarter inch before every burn.",
    "Extreme close-up of small scissors trimming a blackened cotton wick down short on a cream candle in a glass jar on the wooden table."),
 br("n_h9b","It stops the big sooty flame and makes each candle last hours and hours longer.",
    "Close-up of a neat small steady flame on a freshly trimmed cream candle in a glass jar."),
 br("n_h9c","One quick snip before you light it, and that is real money back in your pocket.",
    "Extreme close-up of a hand snipping a candle wick with small scissors over a glass jar on the wooden table."),
 # HACK 10 labels
 br("b13-hack10","And hack ten. Make your own labels at home with plain kraft paper and a simple stamp.",
    "Close-up of hands pressing a rubber stamp onto a small brown kraft paper label, then smoothing the finished label onto a cream candle jar on the wooden table, twine and scissors nearby."),
 br("n_h10b","It looks boutique, it costs you pennies, and people will pay more for a candle that looks handmade.",
    "Close-up of a finished cream candle in a glass jar wearing a stamped kraft paper label, styled neatly on the rustic wooden table."),
 br("n_h10c","A little twine and a sprig of dried lavender, and suddenly it looks like it belongs in a fancy shop.",
    "Close-up of hands tying natural twine and a sprig of dried lavender around a kraft-labeled cream candle jar."),
 # RECAP + CTA + OUTRO
 br("n_recap1","So there they are. Ten little changes that quietly put hundreds of dollars back in my pocket.",
    "Slow wide close-up pan across the full rustic wooden table covered in finished candles, supplies, twine and dried botanicals by the bright window."),
 br("n_recap2","None of them are hard, and you can start with just one of them this weekend.",
    "Close-up of two hands gently lighting a single finished cream candle on the wooden table."),
 ch("b14-cta","If even one of these saves you money, tell me in the comments which candle you are making next. I read every single one.",
    "Starting from the reference image, keep the woman, her blue knit sweater, glasses, curly grey hair and the candle workshop exactly as shown. She leans in slightly toward the camera, smiling warmly with both hands resting on the wooden table beside the finished candles."),
 br("b15-outro","Happy candle making, my friend. I will see you back here at the table.",
    "Warm close-up of a single finished cream candle burning with a gentle flame in a glass jar on the rustic wooden workshop table, shelves of supplies softly visible behind."),
]

REUSED={"b01-hook","b02-intro","b03-hack1","b04-hack2","b05-hack3","b06-hack4",
 "b07-hack5","b08-th1","b09-hack6","b10-hack7","b11-hack8","b12-hack9",
 "b13-hack10","b14-cta","b15-outro"}

M={"title":"The 10 Candle Hacks That Saved Me $100s",
   "channel":"Candice's Candle Corner",
   "narrator_voice":{"provider":"elevenlabs","voiceId":"XH7KR8MDn5xIMYpbfUTx","modelId":"eleven_multilingual_v2"},
   "aspect":"16:9","video_model":"veo-video","reference_photo_url":REF,
   "continuity_bible":BIBLE,"beats":beats}
json.dump(M,open(os.path.join(ROOT,"manifest.json"),"w"),indent=2)

# ---- state surgery ----
sp=os.path.join(ROOT,"state.json"); st=json.load(open(sp))
AUD=os.path.join(ROOT,"audio")
for b in beats:
    bid=b["id"]; s=st["beats"].setdefault(bid,{})
    if b["type"]=="broll":
        s["tts_done"]=False; s.pop("narration_dur",None)
        a=os.path.join(AUD,f"{bid}.mp3")
        if os.path.exists(a): os.remove(a)
    # keep existing 'jobs' (downloaded clips) for reused ids; new ids have none
json.dump(st,open(sp,"w"),indent=2)
new=[b["id"] for b in beats if b["id"] not in REUSED]
print(f"beats={len(beats)} reused={len(REUSED)} new={len(new)}")
print("new:", ", ".join(new))
