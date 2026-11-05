# Kaufman's Adaptive Moving Average — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Core parameters | See `indicators.py` (spec constants) | Published mechanism defaults, not fitted to this window. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 40 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
