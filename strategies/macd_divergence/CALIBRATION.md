# MACD Histogram Divergence — Calibration

All parameters fixed a priori from the MACD spec. No in-sample
sweep, nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| MACD | 12 / 26 / 9 | the Appel standard, unchanged |
| Zigzag confirmation | 5 bars each side | the house zigzag standard |
| Divergence | strict price extreme + opposite histogram extreme | no tolerance band: a higher low must be higher, full stop |
| Exit guard | histogram must confirm (cross zero in the trade's direction) before a zero cross back exits | without this, bullish entries exit on the next bar while hist is still negative |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for a momentum turn to develop |
| Target | none | the histogram exit manages the trade |
| Max hold | 120 bars (~5 days) | a divergence that hasn't turned in five days was not a turn |
| Risk | 1% / trade, 3x leverage cap | house standard |

No optimization was performed, and the window in BACKTEST.md must not
be used to tune any of these numbers.
