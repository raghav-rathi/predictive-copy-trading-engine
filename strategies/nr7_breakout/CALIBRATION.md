# NR7 Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| NR window | 7 bars | Spec. Crabel's NR7 definition. |
| Setup validity | 24 bars | Spec. One day of 1h bars to break out. |
| Range metric | high - low | Spec. Crabel's range definition. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 20 | 7 bars for the NR7 window + ATR(14) + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
