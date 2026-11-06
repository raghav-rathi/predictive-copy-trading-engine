# Fractal Dimension Index — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| FDI window | 30 bars | Spec window. |
| Trending threshold | FDI < 1.4 | Clean-trend regime (below the 1.5 ranging line). |
| Choppy exit threshold | FDI > 1.5 | Ranging/choppy regime. |
| Direction filter | SMA(20) cross | Trend direction; entry only on the cross while FDI < 1.4. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 40 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
