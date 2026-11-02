# RAVI — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Fast / slow SMA | 7 / 65 | Spec. Chande's RAVI periods (65 = one quarter of sessions). |
| Reference lines | +0.3 / -0.3, exit at 0 | Spec. Chande's published reference lines. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 80 | 65 bars for SMA(65) + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
