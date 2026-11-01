# Volume Price Trend — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Contribution | volume x % change | Spec. The PVT definition. |
| Signal line | SMA(20) of PVT | Spec. The standard PVT signal average. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 40 | 20 bars for the PVT average + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
