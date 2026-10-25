# SMA Crossover — Calibration

All parameters fixed a priori from the textbook crossover spec. No
in-sample sweep, nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| Fast / slow SMA | 20 / 50 | the standard medium-term crossover pair |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy stop for a whipsaw-prone signal; trail rides real trends |
| Target | none | the opposite cross is the exit |
| Max hold | 168 bars (~7 days) | a cross that hasn't run in a week is dead |
| Risk | 1% / trade, 3x leverage cap | house standard |

No optimization was performed, and the window in BACKTEST.md must not
be used to tune any of these numbers.
