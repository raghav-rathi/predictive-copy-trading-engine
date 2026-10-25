# ATR Channel Breakout — Calibration

All parameters fixed a priori from the volatility-channel spec. No
in-sample sweep, nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| Midline | SMA(20) | the original ATR-band construction (vs Keltner's EMA) |
| ATR window / mult | 14 / 1.5x | canonical ATR window; 1.5x keeps the channel tight enough to break |
| Stop / trail | 2xATR / 3xATR | trail wider than the stop: give real breakouts room |
| Target | none | the midline exit manages the trade |
| Max hold | 120 bars (~5 days) | a breakout that hasn't run in five days failed |
| Risk | 1% / trade, 3x leverage cap | house standard |

No optimization was performed, and the window in BACKTEST.md must not
be used to tune any of these numbers.
