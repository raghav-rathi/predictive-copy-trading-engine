# Acceleration Bands

Price Headley Acceleration Bands (20, factor 4): upper = SMA(20) of high*(1+4*(h-l)/(h+l)), lower = SMA(20) of low*(1-4*(h-l)/(h+l)), midline = SMA(20) of close. Two consecutive closes outside a band start an acceleration phase (entry); the first close back inside ends it (exit).

## Rules

- Long: two consecutive closes above the upper band.
- Short: two consecutive closes below the lower band.
- Exit: first close back inside the broken band (plus ATR stop / trail).

## Source

- Acceleration Bands (Price Headley): https://www.luxalgo.com/library/concept/acceleration-bands/

Paper only, no live execution.
