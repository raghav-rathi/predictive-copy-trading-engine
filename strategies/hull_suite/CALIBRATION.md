# Hull Suite — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| HMA period | 16 | Spec. Half 8 / full 16 / smoothing 4 = sqrt(16). |
| Signal | HMA slope turn | Spec. The Suite's own turn rule, not a price cross. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 32 | 16 bars for HMA + 4-bar smoothing + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
