# Triangle Breakout — Calibration

All parameters fixed a priori from the textbook pattern spec. No
in-sample sweep, nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| Zigzag confirmation | 5 bars each side | the house zigzag standard |
| Flat-side tolerance | 1% | "flat" must mean flat — 1% is strict on purpose |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | house continuation-pattern standard |
| Target | none | the reclaim exit manages the trade |
| Max hold | 96 bars (~4 days) | a triangle breakout that hasn't run in four days failed |
| Risk | 1% / trade, 3x leverage cap | house standard |

No optimization was performed, and the window in BACKTEST.md must not
be used to tune any of these numbers.
