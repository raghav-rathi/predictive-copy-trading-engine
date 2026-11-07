# MACD Zero-Line Cross — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| MACD fast / slow / signal | 12 / 26 / 9 | Standard MACD parameters from the source. |
| Entry | Zero-line cross of the MACD line | Spec. |
| Exit | Reverse zero-line cross | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No spec corrections, no bug fixes requiring re-runs, no PnL-selected tuning.
