# CG Oscillator

John Ehlers' Center of Gravity oscillator treats the last 10 closes
as a mass distribution: where its center of gravity sits relative
to the window midpoint tells you which way price is leaning, with
almost no lag. The CG / trigger-line cross is the signal.

## Mechanism

- Centroid = Σ weight × close / Σ close over 10 bars, oldest
  bar weighted 10, newest weighted 1.
- CG = 5.5 − centroid position: 0 for flat prices, positive when
  recent prices sit above the window's center of mass.
- Trigger line = SMA(3) of CG; crosses are the trade signals.

## Entry / exit

- **Long entry:** CG crosses above its trigger line.
- **Short entry:** CG crosses below its trigger line.
- **Exit:** the opposite cross. The risk layer adds a 2xATR stop, a
  2.5xATR trail, and a 120-bar max hold.

## Source

- Center of Gravity Oscillator (John Ehlers):
  https://admiralmarkets.com/education/articles/forex-indicators/trading-with-the-center-of-gravity-indicator

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 20 bars
(12 bars for the centroid + trigger + ATR/margin.).

## Honest limitation

A 10-bar centroid is extremely responsive — that is the selling
point and the failure mode. On 1h crypto bars it flips on every
local wiggle, and the 3-bar trigger adds almost no smoothing, so
the cross count is very high and fees dominate (see BACKTEST.md).

Paper only, no live execution.
