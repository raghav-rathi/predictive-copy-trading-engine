# MA Envelope Breakout — Calibration

All parameters fixed a priori from the envelope spec. No in-sample
sweep, nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| Midline | SMA(20) | the envelope's anchor |
| Envelope | +/- 5% | wide for 1h bars on purpose: rarity is the thesis |
| ATR window | 14 | canonical (risk layer only) |
| Stop / trail | 2xATR / 2.5xATR | house breakout standard |
| Target | none | the midline exit manages the trade |
| Max hold | 120 bars (~5 days) | a breakout that hasn't run in five days failed |
| Risk | 1% / trade, 3x leverage cap | house standard |

No optimization was performed, and the window in BACKTEST.md must not
be used to tune any of these numbers.
