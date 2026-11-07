# DEMA Crossover — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| DEMA | DEMA(n) = 2*EMA(n) - EMA(EMA(n)) | Spec (Mulloy, 1994). |
| Fast / slow | DEMA(12) / DEMA(26) | Spec. |
| Entry | Fast crosses above slow (long) / below slow (short) | Spec. |
| Exit | Reverse cross | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No spec corrections, no bug fixes requiring re-runs, no PnL-selected
tuning.
