# Bollinger W-Bottom / M-Top

John Bollinger's W-bottom (*Bollinger on Bollinger Bands*, 2001):
price makes a first low outside the lower band, rallies toward the
middle band, then makes a second low that may be lower in price but
holds inside the band — the second push down is weaker relative to
volatility, shown by a higher %B. The M-top is the exact mirror at
the upper band.

## Rules

- **Bands:** BB(20, 2.0); %B = (close − lower) / (upper − lower).
- **W-bottom (long):**
  1. First low: a bar with %B < 0 (the most extreme such bar while
     waiting counts as the first low).
  2. Rally: a later bar closes above the middle band.
  3. Second low: within 40 bars of the rally, a bar whose close is
     lower than or within 1% of the first low's close AND whose %B
     is higher than the first low's %B.
  4. Long entry: the first close above the middle band after the
     second low.
- **M-top (short):** exact mirror — first high %B > 1, dip below the
  middle band, second high within 40 bars whose close is higher
  than or within 1% of the first high's close with a LOWER %B,
  entry on the first close below the middle band.
- **Long exit:** close below the middle band.
- **Short exit:** close above the middle band.
- ATR stop / trail from the risk layer also applies; max hold 120 bars.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- John Bollinger, *Bollinger on Bollinger Bands* (2001)
- Bollinger Bands official site: https://www.bollingerbands.com/bollinger-bands
- W-bottom explainer (first low outside the band, second low inside,
  higher %B): https://velotrade.com/blog/bollinger-bands
- %B convention shared with `strategies/bollinger_pctb` in this repo.

Paper only, no live execution.
