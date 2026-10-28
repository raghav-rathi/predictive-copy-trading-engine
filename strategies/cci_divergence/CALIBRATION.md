# CCI Divergence — Calibration

All parameters fixed a priori from the Lambert CCI spec and the
textbook divergence setup. No in-sample sweep, nothing selected
on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| CCI period | 20 | Lambert's original period, unchanged |
| Mean deviation | around the current bar's SMA | Lambert's definition; a rolling mean of per-bar deviations delays CCI by 20 bars and must not be used |
| Pivot window | ±2 bars, 2-bar lag | a pivot must be confirmed by bars on both sides; the lag is what makes it causal |
| Divergence window | 40 bars | the two pivots must belong to the same move, not two different regimes |
| Confirmation | close above the prior 3-bar high (bullish) / below the prior 3-bar low (bearish), within 20 bars of the second pivot | price must confirm the oscillator's story promptly, or the divergence is stale |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for a momentum turn to develop |
| Target | none | the opposite-divergence exit manages the trade |
| Max hold | 168 bars (~7 days) | a divergence that hasn't turned in a week was not a turn |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the confirmation rule is the weakest link —
a 3-bar high is a low bar that fires on noise. Requiring a
stronger confirmation (e.g. a close above the intervening pivot
high) would cut trades sharply and is the only change with a
plausible story for fixing the BTC leg, but it was not tested
here and must not be fitted to this window.

**Verdict: loser.** -$962 combined over 156 trades, driven by
a -$1,908 BTC leg. Do not trade this as shipped.
