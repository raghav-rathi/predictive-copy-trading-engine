# Aroon Oscillator — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Aroon period | 25 | Spec. Chande's standard Aroon window. |
| Entry / exit | zero cross | Spec. The oscillator's regime line. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 39 | 25 bars for Aroon + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
