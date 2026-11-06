# Volume-weighted MACD — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Volume-weighted price window | 20 bars | Standard volume-weighting window. |
| MACD fast / slow / signal | 12 / 26 / 9 | Standard MACD parameters. |
| Trend filter | SMA(50) of close | Standard trend filter. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 60 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
