# Flag Pattern Breakout — Calibration

All parameters fixed a priori from the textbook pattern spec. No
in-sample sweep, nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| Pole | >=3xATR in <=12 bars, stalled | a pole must be sharp AND finished; the stall rule stops mid-trend triggers |
| Consolidation | 5–15 bars | shorter is noise, longer is not a flag anymore |
| Consolidation range | <=1.5xATR | a flag is tight by definition |
| Max retrace | 60% of pole | deeper retracement means the pole failed, not consolidated |
| Fail distance | 0.5xATR past far side | invalidation must be decisive, not a wick |
| ATR window | 14 | canonical |
| Stop / trail | 1.5xATR / 2xATR | tighter house variant: flags are fast patterns |
| Target | none | the reclaim exit manages the trade |
| Max hold | 72 bars (~3 days) | a flag breakout that hasn't run in three days is a failed flag |
| Risk | 1% / trade, 3x leverage cap | house standard |

No optimization was performed, and the window in BACKTEST.md must not
be used to tune any of these numbers.
