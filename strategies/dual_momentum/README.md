# Dual Momentum

Gary Antonacci's Dual Momentum Investing (*Dual Momentum Investing*,
2014): combine absolute momentum (trend-following: is the asset
itself rising?) with relative momentum (relative strength: is it
rising faster than the alternatives?). Antonacci's original system
ranks US equities vs bonds on 12-month returns and holds the
winner only while its absolute momentum is positive, otherwise
moving to bonds. This is the 1h crypto adaptation over the
BTC/ETH/HYPE basket.

## Rules

- **Absolute momentum:** 240-bar log return of the close
  (~10 days on 1h bars — the adaptation of Antonacci's 12-month
  lookback; see CALIBRATION.md).
- **Relative momentum:** the coin's 240-bar log return minus the
  equal-weight basket's 240-bar log return (mean of the three
  coins' 240-bar log returns).
- **Long entry:** the coin becomes the top-ranked coin by relative
  momentum while its absolute momentum is positive.
- **Short entry:** the coin becomes the bottom-ranked coin by
  relative momentum while its absolute momentum is negative.
- **Long exit:** the coin stops being top-ranked (rank flip) or
  its absolute momentum turns non-positive.
- **Short exit:** the coin stops being bottom-ranked or its
  absolute momentum turns non-negative.
- Otherwise the system is flat in that coin. The harness risk
  layer's 2xATR stop / 2.5xATR trail also applies; max hold
  120 bars.
- Parameters are Antonacci's published defaults as adapted in
  CALIBRATION.md; nothing was tuned to this window.

All computation is causal, so signals on bar i use only data
through bar i's close.

## Source

- Gary Antonacci, *Dual Momentum Investing* (2014):
  https://www.optimalmomentum.com/ (verified loading 2026-11-13)

Paper only, no live execution.
