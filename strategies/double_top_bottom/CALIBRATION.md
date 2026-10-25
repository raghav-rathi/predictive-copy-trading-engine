# Double Top / Double Bottom — Calibration

All parameters fixed a priori from the textbook pattern spec. No
in-sample sweep, nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| Zigzag confirmation | 5 bars each side | the house zigzag standard |
| Extreme tolerance | 1.5% | two tests of "the same level" must actually agree |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for a reversal to develop; trail rides it |
| Target | none | the reclaim exit manages the trade |
| Max hold | 96 bars (~4 days) | a neckline break that hasn't run in four days was not a reversal |
| Risk | 1% / trade, 3x leverage cap | house standard |

No optimization was performed, and the window in BACKTEST.md must not
be used to tune any of these numbers.
