# Rectangle Breakout — Calibration

All parameters fixed a priori from the textbook rectangle
description. No in-sample sweep, nothing selected on the backtest
window.

| Parameter | Value | Rationale |
|---|---|---|
| Range window | 20 bars | long enough to be a real consolidation on 1h, short enough to occur often |
| Max width | 4% of price | textbook "narrow" range; wide enough to catch crypto ranges, tight enough to exclude trends |
| Min hold | 15 bars | a range must persist, not flash for a bar or two |
| Volume filter | > 1.2x 20-bar average | textbook confirmation: breakouts need participation |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for a breakout to breathe, trail to protect follow-through |
| Target | none | the opposite-boundary exit manages the trade |
| Max hold | 168 bars (~7 days) | a breakout that hasn't run in a week was not a breakout |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the trade count is dominated by the width and
hold thresholds — loosening either adds many marginal ranges
(and, on this window, mostly more losing breakouts). Tightening
either starves the strategy of trades without evidence it would
improve the win rate.

**Verdict: loser.** -$1,266 combined over 229 trades, PF below
1 on two of three coins. Do not trade this as shipped.
