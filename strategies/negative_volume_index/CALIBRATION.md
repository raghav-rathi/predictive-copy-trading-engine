# Negative Volume Index — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Start value | 1000 | Spec. The conventional NVI origin. |
| Update rule | falling-volume bars only | Spec. Dysart/Fosback definition. |
| Signal line | EMA(255) | Spec. The classic NVI signal line. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 300 | 255 bars for the EMA(255) + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
