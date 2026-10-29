# RSI Failure Swing — Calibration

All parameters fixed a priori from the Wilder/Cardwell spec.
No in-sample sweep, nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| RSI period | 14 | Wilder's original period, unchanged |
| Oversold / overbought | 30 / 70 | Wilder's failure-swing thresholds |
| Pivot window | ±2 bars, 2-bar lag | a pivot must be confirmed by bars on both sides; the lag is what makes it causal |
| Second-low rule | strictly higher than the first low (bullish) | the "failure" itself; a lower second low means momentum is not spent |
| Trigger | RSI breaks the intervening swing extreme | price confirmation is deliberately NOT required — this is an oscillator-structure trade |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for a momentum turn to develop |
| Target | none | the opposite-swing exit manages the trade |
| Max hold | 168 bars (~7 days) | a swing that hasn't turned in a week was not a turn |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the 30/70 thresholds are the binding
constraint — most 1h RSI swings never reach them, which is why
the strategy trades only ~100 times in 7 months. Loosening to
40/60 would multiply trades but would no longer be a failure
swing (it would be ordinary RSI range trading), so it was not
tested here and must not be fitted to this window.

**Verdict: loser.** -$2,310 combined over 100 trades, red on
all three coins. Do not trade this as shipped.
