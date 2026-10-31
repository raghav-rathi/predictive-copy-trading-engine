# Choppiness Index

Dreiss Choppiness Index regime filter + Donchian breakout — the
indicator itself is directionless, so it supplies the regime gate
while the Donchian bands supply the direction.

## Mechanism

- **CHOP(14):** CHOP = 100 * log10( sum(TR, 14) / (MaxHi14 - MinLo14) )
  / log10(14), where TR is the true range and MaxHi14 / MinLo14 are
  the highest high / lowest low over 14 bars. Low readings mean price
  is covering ground efficiently (trending); high readings mean it is
  wandering inside its range (choppy). A zero window range (flat
  prices) emits NaN rather than dividing by zero.
- **Donchian(20), prior-bar only:** the bands on bar i are the max high
  / min low over bars i-20..i-1 (the rolling bands shifted by 1), so
  the current bar's own high/low can never trigger its own breakout.

## Entry / exit

- **Long entry:** CHOP < 38.2 (trending regime) AND close crosses above
  the prior Donchian(20) high.
- **Short entry:** CHOP < 38.2 AND close crosses below the prior
  Donchian(20) low.
- **Long exit:** CHOP crosses above 61.8 (regime turns choppy) OR close
  crosses below the prior Donchian low.
- **Short exit:** CHOP crosses above 61.8 OR close crosses above the
  prior Donchian high.
- The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max
  hold.

## Source

- Choppiness Index, E.W. Dreiss (formula, 14-bar default, 38.2 / 61.8
  Fibonacci thresholds):
  https://www.LuxAlgo.com/library/concept/choppiness-index/
  (verified; the Donchian-breakout pairing and the exit rules are this
  strategy's own construction, not the source's.)

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1% equity
risk per trade, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
longs and shorts allowed. WARMUP = 30 bars (Donchian(20) prior-bar
bands need 21 bars, CHOP(14) needs 14, ATR(14) needs 14).

## Honest limitation

CHOP is a lagging regime gauge: by the time it drops below 38.2 the
trend that produced the reading is already underway, so entries chase
moves that may be exhausted — and a breakout that itself creates the
low CHOP reading can reverse straight back through the opposite band.
The backtest (BACKTEST.md) shows the stop managing 81% of exits, i.e.
most entries do not survive to a signal exit.

Paper only, no live execution.
