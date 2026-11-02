# OBV Cross — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| OBV EMA | 20 | Spec. A standard smoothing for a cumulative flow line. |
| Entry / exit | OBV vs EMA cross | Spec. Granville's confirmation cross. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 34 | 20 bars for the OBV EMA + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
