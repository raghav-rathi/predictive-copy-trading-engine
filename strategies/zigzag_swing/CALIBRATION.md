# ZigZag Swing Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Deviation | 5% | Spec. The classic ZigZag deviation for swing filtering. |
| Levels | last confirmed pivots only | Spec. No repainting: unconfirmed extremes are never traded. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 30 | 5% pivot confirmation + ATR/margin (pivot timing varies). |

No bug fixes requiring re-runs, no PnL-selected tuning.
