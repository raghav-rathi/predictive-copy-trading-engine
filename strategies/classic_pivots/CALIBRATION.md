# Classic Pivot Breakout — Calibration

All parameters fixed a priori from the pivot spec. No in-sample
sweep, nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| Levels | PP/R1/S1 from prior bar | the classic formula, refreshed hourly |
| ATR window | 14 | canonical (risk layer only) |
| Stop / trail | 1.5xATR / 2xATR | tighter house variant: pivot levels are one bar wide |
| Target | none | the PP exit manages the trade |
| Max hold | 72 bars (~3 days) | a pivot breakout that hasn't run in three days is noise |
| Risk | 1% / trade, 3x leverage cap | house standard |

No optimization was performed, and the window in BACKTEST.md must not
be used to tune any of these numbers.
