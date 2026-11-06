# Wilder Volatility Stop — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| ATR window | 7 | Wilder's Volatility Stop as published. |
| Stop multiplier | 3.0x ATR | Wilder's Volatility Stop as published. |
| Initial-trend filter | SMA(20) | Spec: trend at warmup from close vs SMA(20). |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 30 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
