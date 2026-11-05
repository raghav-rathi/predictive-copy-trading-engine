# Hull MA Crossover — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| HMA fast / slow | 16 / 32 | Common published HMA crossover pair. |
| HMA smoothing length | round(sqrt(n)) — 4 for n=16, 6 for n=32 | Hull's definition (sqrt(n), rounded to an integer window). |
| WMA weights | linear 1..n | Standard WMA definition. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 40 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
