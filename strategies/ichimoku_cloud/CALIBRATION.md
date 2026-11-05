# Ichimoku Cloud — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Tenkan / Kijun / Senkou | 9 / 26 / 52 | Published Ichimoku standard (Hosoda). |
| Chikou confirmation | c > c.shift(26) (long) | Lookahead-free equivalent of the Chikou span check. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 80 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
