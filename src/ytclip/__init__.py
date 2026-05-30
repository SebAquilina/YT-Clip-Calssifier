"""YT-Clip-Classifier: classify what happens in every 5-10s window of a DIY video.

Pipeline: download (or storyboard) -> segment into <=10s windows -> build
montages -> vision-classify each window against a candle-DIY taxonomy ->
rules-engine smoothing -> JSON timeline + markdown report.
"""

__version__ = "0.1.0"
