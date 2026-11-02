# Adaptive RSI — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| RSI period | 14 | Spec. Wilder's standard RSI window. |
| Efficiency window | 10 | Spec. Kaufman's ER window. |
| Fast / slow constants | 2/3 / 2/31 | Spec. Kaufman's 2-day / 30-day smoothing constants, squared. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 30 | 14 bars for RSI + 10-bar efficiency ratio + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
