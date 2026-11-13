# Smash Day

Larry Williams' Smash Day (*Long-Term Secrets to Short-Term Trading*,
1999): a big-range day followed by an inside (contraction) day sets up a
trade on the break of the inside day's high or low. The logic is
volatility compression: the wide day expends energy, the inside day is
the market catching its breath, and the break of the inside range is
the resumption — in the direction of the break, not the wide day.

## Rules

- **Setup:** a UTC day whose range is > 1.5x the trailing 20-day mean
  daily range (wide day), followed by a day whose high is below the wide
  day's high and whose low is above the wide day's low (inside day).
- **Long entry:** a smash setup is active and a 1h close crosses above
  the inside day's high.
- **Short entry:** a smash setup is active and a 1h close crosses below
  the inside day's low.
- **Long exit:** close crosses back below the inside day's low (failed
  break).
- **Short exit:** close crosses back above the inside day's high.
- The setup is valid for the two days after the inside day (Williams
  trades the next day; the second day is allowed because a 1h-bar break
  can arrive late on 24/7 crypto — fixed a priori, not tuned).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail plus the opposite-break
  exit. Max hold 120 bars.
- Parameters are Williams' published ones (1.5x range multiple,
  20-day mean range, inside-day definition); nothing was tuned to this
  window.

All computation is causal: for a 1h bar in UTC day d, only completed
days d-1, d-2, ... are used. Days are UTC calendar days — crypto trades
24/7, so there is no session open to anchor to; the UTC day is the
documented adaptation of Williams' daily-bar system.

## Source

- Larry Williams, *Long-Term Secrets to Short-Term Trading* (1999), Smash Day chapter: https://www.investopedia.com/terms/i/insideday.asp

Paper only, no live execution.
