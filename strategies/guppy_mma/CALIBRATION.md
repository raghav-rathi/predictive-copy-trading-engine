# Guppy MMA — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Short group | 3/5/8/10/12/15 | Spec. Guppy's standard fast periods. |
| Long group | 30/35/40/45/50/60 | Spec. Guppy's standard slow periods. |
| Ribbon center | mean of each group | Spec. The group mean is the ribbon line traded. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 70 | 60 bars for EMA(60) + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
