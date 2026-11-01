# DPO Cross — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| DPO period | 20 | Spec. The standard DPO period. |
| Displacement | 11 = 20/2 + 1 | Spec. Centers the average in its window. |
| Signal | zero cross | Spec. The textbook DPO trend signal. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 40 | 31 bars for the displaced SMA(20) + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
