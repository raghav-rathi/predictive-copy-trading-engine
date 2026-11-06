# EMA Pullback — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Trend / pullback EMAs | EMA(20), EMA(50) | Classic trend-following pair. |
| ATR window | 14 | Standard ATR length. |
| Touch band | long low in [EMA20 − 1.0×ATR, EMA20 + 0.5×ATR] (mirror for shorts) | Spec: pullback reaches the EMA band without breaking far through it. |
| Touch lookback | 5 bars | Spec: recent pullback, not a stale one. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 60 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
