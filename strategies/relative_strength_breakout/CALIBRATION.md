# Relative Strength Breakout — Calibration

All parameters fixed a priori from the ratio-line breakout
setup. No in-sample sweep, nothing selected on the backtest
window.

| Parameter | Value | Rationale |
|---|---|---|
| Benchmark | BTC 1h closes | the market's base asset; the ratio isolates coin-specific strength |
| Ratio range | prior 20 bars, current bar excluded | a breakout must beat a range it did not help form |
| Exit reference | 20-bar mean ratio | same window as the range, so exit means the breakout leg fully faded |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for a ratio breakout to extend |
| Target | none | the mean-fade exit manages the trade |
| Max hold | 168 bars (~7 days) | a relative-strength leg that hasn't extended in a week is stale |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the 20-bar range is the whole trade — a
shorter range would fire on ratio noise (more churn, worse
fees), a longer range would fire only on the largest
relative moves (fewer, later entries). The stop dominance
(334 of 531 exits) suggests the range breakout, at any
nearby length, is mostly noise on 1h; that is a property of
the idea, not a parameter to fit.

**Verdict: loser.** -$3,610 combined over 531 traded-leg
trades (BTC benchmark leg: 0 trades by construction, excluded).
Do not trade this as shipped.
