# Z-Score Reversion — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Lookback | 20 | Spec. The Bollinger standard. |
| Entry | |z| = 2 | Spec. The documented z-score entry level. |
| Exit | z = 0 | Spec. The documented reversion-to-mean exit. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 30 | 20 bars for SMA/std(20) + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
