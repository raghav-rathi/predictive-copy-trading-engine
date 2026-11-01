# RVI Cross — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Weighting | (1,2,2,1)/6 | Spec. Ehlers' published RVI smoothing. |
| Smooth period | 10 | Spec. The standard RVI lookback. |
| Signal line | (1,2,2,1) of RVI | Spec. Ehlers' published signal line. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 20 | 13 bars for the weighted SMA(10) + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
