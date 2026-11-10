# Chande Dynamic Momentum Index — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Volatility window | stddev(close, 5), sample std (ddof=1) | Chande's spec via the Wickra reference; 5-bar window is the published constant. |
| Volatility average | SMA(vol, 10) | Chande's spec; 10-bar average of the 5-bar stddev. |
| Vi | vol / vol_avg; 1.0 if vol_avg is 0 or NaN | Spec rule; a zero/undefined average means "average volatility", i.e. the base lookback. |
| Base period | 14 | Chande's constant; TD = 14 when volatility is at its own average. |
| TD clamp | [5, 30] | Chande's published clamp on the dynamic lookback. |
| DMI | 100 * mean(gains) / (mean(gains) + mean(losses)) over the last TD close-to-close changes; simple means, not Wilder smoothing; 50 if gains + losses == 0 | Wickra reference implementation of Chande's spec; DMI bounded [0, 100]. |
| Long entry | DMI crosses up through 30 | RSI-style oversold cross; Chande: use DMI "much the same as the RSI". |
| Short entry | DMI crosses down through 70 | RSI-style overbought cross. |
| Long exit | DMI crosses above 70 | Overbought extreme. |
| Short exit | DMI crosses below 30 | Oversold extreme. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 45 | Max TD (30) + volatility-average warmup (14) + margin; first valid DMI needs i >= TD. |

## Spec deviations

- **Vi = 0 (zero current volatility, positive average):** the spec
  formula 14 / Vi divides by zero. Implemented as the faithful
  limit: 14 / 0 → +∞, clamped to TD = 30 (the maximum lookback).
  This occurs transiently when price goes flat after a volatile
  stretch; verified by test
  (`test_td_clamp_ceiling_when_volatility_dies`).
- **DMI window definition:** "RSI over TD bars" is implemented as
  the last TD close-to-close changes (indices i−TD+1 … i), i.e. the
  TD changes ending at bar i's close. DMI is NaN until i >= TD.
  No other reading of the window is possible without lookahead.
- **stddev convention:** sample stddev (ddof=1, pandas default) is
  used for the 5-bar volatility; the published references do not
  state the ddof, and the choice is immaterial to Vi (a constant
  scale factor cancels in the ratio) except through the rounding
  of TD at boundaries.

No bug fixes requiring re-runs, no PnL-selected tuning.
