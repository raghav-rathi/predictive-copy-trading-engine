# Head and Shoulders — Calibration

All parameters fixed a priori from the textbook pattern spec. No
in-sample sweep, nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| Zigzag confirmation | 5 bars each side | the house zigzag standard |
| Shoulder tolerance | 3% | shoulders must be "roughly equal" — 3% is the textbook slack |
| Neckline | lower trough / higher peak | the conservative trigger (a break of the nearer level is weaker evidence) |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for a reversal to develop; trail rides it |
| Target | none | the reclaim exit manages the trade |
| Max hold | 120 bars (~5 days) | H&S formations take longer to resolve than double tops |
| Risk | 1% / trade, 3x leverage cap | house standard |

No optimization was performed, and the window in BACKTEST.md must not
be used to tune any of these numbers.
