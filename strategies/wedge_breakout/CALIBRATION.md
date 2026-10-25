# Wedge Breakout — Calibration

All parameters fixed a priori from the textbook pattern spec. No
in-sample sweep, nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| Zigzag confirmation | 5 bars each side | the house zigzag standard |
| Wedge span | 80 bars | all four pivots must be recent, or the "wedge" is stale structure |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | house reversal-pattern standard |
| Target | none | the reclaim exit manages the trade |
| Max hold | 96 bars (~4 days) | a wedge breakout that hasn't run in four days failed |
| Risk | 1% / trade, 3x leverage cap | house standard |

No optimization was performed, and the window in BACKTEST.md must not
be used to tune any of these numbers.
