# Wedge Breakout

Converging trendlines through the last two swing highs and the last
two swing lows. Rising wedge: higher highs and higher lows with the
highs rising slower than the lows (the lines converge upward) — it
breaks down, traded short. Falling wedge: lower highs and lower
lows with the highs falling faster (converging downward) — it breaks
up, traded long. Trendlines are fit through two pivots each: no
regression, no fitted parameters beyond the pivot window.

## Rules

- Rising wedge pending: high slope > 0, low slope > 0, high slope <
  low slope. Short on a close below the lower trendline.
- Falling wedge pending: high slope < 0, low slope < 0, high slope <
  low slope (highs fall faster). Long on a close above the upper
  trendline.
- Invalidation: rising wedge clears if price breaks above the upper
  line; falling wedge clears if price breaks below the lower line.
- Exit: close back inside the entry trendline level, or the
  opposite wedge's breakout. The entry level is frozen at the entry
  bar — the line keeps moving after entry, but the exit level does
  not.
- Risk: 2xATR stop, 2.5xATR chandelier trail, no fixed target,
  96-bar (4-day) max hold, 1% equity risk per trade, 3x leverage cap

Source: rising / falling wedges (Bulkowski, Encyclopedia of Chart
Patterns).
