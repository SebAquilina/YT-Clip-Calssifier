#!/usr/bin/env python3
"""Enrichment pass: replace B-roll narration with longer, richer sentences so the
~10-minute target is hit, and clear their tts_done so narration regenerates.
The SHOTS are unchanged, so the already-generated primary clips still match; the
longer narration makes each beat ~12-15s, which triggers a 2nd (alternate-angle)
clip in generate.py. Character spoken lines are left short and untouched."""
import json, os
ROOT=os.path.dirname(os.path.abspath(__file__))
LONG={
"h00-hook":"Last month, one hundred candles came out of my workshop with something wrong with every single one, and instead of binning a whole month of work, I sat down and fixed all one hundred by hand.",
"b_int1":"Sunken tops, frosted cloudy sides, and wicks that had drowned sideways in the wax. A whole month of pouring, and not one of them was fit to sell the way it was.",
"b_int1b":"I lined them all up and counted them twice just to be sure, and there it was, one hundred candles, every one carrying some little flaw I had caused without even realising it.",
"b_int2":"But fixing a hundred mistakes back to back, one after another, taught me far more about making a good candle than ten quiet years of getting it mostly right ever did.",
"l1a":"The very first defect was on nearly every jar. Ugly wet-looking patches and pale cloudy frosting, right where the wax had shrunk and pulled itself away from the cold glass as it set.",
"l1b":"It turns out the cause is almost always cold glass, so now before I pour a single candle I warm every empty jar through in a low oven until the glass is gently warm to the touch.",
"l1c":"Warm glass and warm wax settle against each other slowly and bond all the way down, and just like that those wet spots and that frosting vanish completely, every single time.",
"l2a":"The next defect I kept finding was deep sinkholes. As the candle cooled it would shrink inward and crack open a hollow crater right down around the wick, leaving an ugly pit on top.",
"l2b":"That one comes from pouring your wax far too hot, so now I let it cool in the pitcher to about a hundred and thirty-five degrees, checking it with a little thermometer before I pour.",
"l2c":"And once it has set, one thin, slow second pour floods that dip back up and leaves you with a flat, glassy, professional-looking top instead of a sunken hole.",
"l2d":"Honestly, pouring slow and low, never hot and fast, is the single biggest secret to a smooth, level, glassy candle surface every time.",
"l3a":"About half of my batch had a weak, patchy scent, and when I traced it back the reason was almost embarrassing. I had been pouring the fragrance oil in by eye, just glugging it from the bottle.",
"l3b":"A four dollar kitchen scale fixed it overnight. Now I weigh the melted wax first, then I weigh in exactly ten percent fragrance oil, so the ratio is perfect in every batch I make.",
"l3c":"And the difference is night and day. Every candle now smells exactly as strong as the last one, batch after batch after batch, with no more weak ones and no more wasted oil.",
"l4a":"So many of my candles had set with the wick frozen hard against one side of the glass, which makes them burn down lopsided, tunnel badly, and look careless on the shelf.",
"l4b":"The fix costs about a dollar for a whole bag. I simply lay a plain wooden clothespin across the rim of each jar so it pinches the wick and holds it dead centre while the wax sets.",
"l4c":"I rest one across every single jar, then I walk away and leave them overnight, and in the morning every wick is standing perfectly straight and centred, ready to burn evenly.",
"l4d":"No more crooked, leaning wicks quietly ruining a candle that was otherwise absolutely perfect.",
"l5a":"And the handful of candles I genuinely could not rescue? I did not throw away so much as a single gram of the wax that was inside them.",
"l5b":"I scooped the old wax out of every ruined jar and saved it in an old tin, and once it was full I melted the whole lot back down and poured it into brand new layered candles, completely free.",
"l5c":"And here is the funny part. Those rescued scrap candles, with their soft uneven layers, are now the ones my regular customers ask for by name.",
"l6a":"Some of my candles smelled absolutely wonderful while they were cold, but the moment you lit them they threw almost no scent into the room at all, which baffled me for ages.",
"l6b":"The fix is simply patience. Now every candle I make has to cure, sitting quietly on a shelf for two full weeks, before I will ever let it be lit or sold.",
"l6c":"That resting time lets the wax and the oil properly bind together, and a cured candle will throw easily twice the scent and fill an entire room instead of just the table it sits on.",
"l7a":"A whole row of mine had burned with huge, smoky, flickering flames that left black soot on the glass and tunnelled straight down the middle, wasting half the wax around the edge.",
"l7b":"The flame was far too big simply because the wick was far too long, so now, every single time before I light one, I trim the wick down to about a quarter of an inch.",
"l7c":"That short little wick gives you a small, calm, clean flame with no soot, and it makes the candle burn down evenly and last for hours and hours longer.",
"l8a":"I also realised that cheap, weak fragrance oil was quietly behind a lot of those disappointing, faint-smelling batches in the first place.",
"l8b":"Buying one really good oil in a proper four ounce bottle actually works out far cheaper per ounce than the tiny sample sizes, and it smells immeasurably better in the finished candle.",
"l9a":"Every jar that came out of a failed candle got a second life on my table instead of being thrown straight into the recycling bin.",
"l9b":"A good long soak in hot soapy water lifts the old set wax cleanly out, and the paper label softens and slides right off without any scrubbing at all.",
"l9c":"And just like that, last week's reject becomes this week's free, perfect, sparkling clean container, ready for a fresh pour.",
"l10a":"The very last fix was the cheapest of the whole lot, and yet it roughly doubled what people were happy to pay me for the exact same candle.",
"l10b":"A square of plain brown kraft paper and one simple rubber stamp turns a bare, anonymous jar into something that genuinely looks like it came from a little boutique.",
"l10c":"Add a loop of natural twine and a single sprig of dried lavender, and suddenly that humble candle looks like it belongs on the shelf of a fancy city shop.",
"b_recap":"Ten small, simple fixes, most of them costing a dollar or less, quietly turned an entire month of expensive disasters into the best-selling, best-smelling batch of candles I have ever made.",
"b_outro":"So be patient with yourself, fix them one at a time, and you will get there. Happy candle making, my friend, and I will see you back here at the table very soon.",
}
m=json.load(open(os.path.join(ROOT,"manifest.json")))
for b in m["beats"]:
    if b["id"] in LONG: b["sentence"]=LONG[b["id"]]
json.dump(m,open(os.path.join(ROOT,"manifest.json"),"w"),indent=2)
sp=os.path.join(ROOT,"state.json"); s=json.load(open(sp)); AUD=os.path.join(ROOT,"audio")
for bid in LONG:
    st=s["beats"].get(bid,{})
    st["tts_done"]=False; st.pop("narration_dur",None)
    a=os.path.join(AUD,f"{bid}.mp3")
    if os.path.exists(a): os.remove(a)
    s["beats"][bid]=st
json.dump(s,open(sp,"w"),indent=2)
print(f"enriched {len(LONG)} narration sentences; cleared their tts_done")
