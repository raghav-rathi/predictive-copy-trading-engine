# Kijun Cross — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Kijun period | 26 | Spec. Standard Ichimoku baseline window. |
| Entry / exit | price vs Kijun cross | Spec. The baseline cross alone, no other Ichimoku filter. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 40 | 26 bars for Kijun-sen + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
