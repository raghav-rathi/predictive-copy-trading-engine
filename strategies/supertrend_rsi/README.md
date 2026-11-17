# Supertrend RSI

Supertrend trend filter plus a Wilder RSI(14) momentum trigger:
only take the trend's side when RSI freshly turns through 50.

## Rules

- **Supertrend(10, 3.0):** standard ATR-based Supertrend, Wilder
  ATR(10). The line is the lower band while direction is up (+1)
  and the upper band while direction is down (-1); direction
  flips when the close crosses the opposing band.
- **RSI(14):** Wilder RSI.
- **Long entry:** close above the Supertrend line AND RSI crosses
  above 50.
- **Short entry:** close below the Supertrend line AND RSI
  crosses below 50.
- **Long exit:** Supertrend flips bearish (direction +1 -> -1).
- **Short exit:** Supertrend flips bullish (direction -1 -> +1).
- The RSI cross is a genuine cross (previous RSI on the old side
  of 50, current RSI on the new side) — RSI merely sitting above
  50 does not enter. Exits use the direction flip rather than a
  raw close-vs-line cross, because the line jumps to the opposite
  band on the flip bar.
- The harness risk layer's 2xATR stop / 2.5xATR trail also
  applies. Max hold 120 bars.
- Warmup 60 bars.

All computation is causal, so signals on bar i use only data
through bar i's close.

## Source

- Supertrend indicator (Olivier Seban); RSI (J. Welles Wilder,
  *New Concepts in Technical Trading Systems*):
  https://www.investopedia.com/supertrend-indicator-7976167

Paper only, no live execution.
