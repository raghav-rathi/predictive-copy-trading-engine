# Mean Reversion Z-Score — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Z-score lookback / entry band / exit | SMA(20) / std(20), +/-2, exit at 0 | Published mechanism defaults, not fitted to this window. |
| Regime guard | SMA(50) slope over 10 bars, flat counts as with-trend | Keeps the fade out of strong trends, per spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 60 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
