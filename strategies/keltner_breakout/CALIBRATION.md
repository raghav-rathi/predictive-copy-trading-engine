# Keltner Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| EMA / ATR | 20 / 10 | Spec. Standard Keltner construction. |
| Band multiplier | 2.0 | Spec. Wider than 1.5 so only real expansions trigger. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 30 | 20 bars for EMA(20) + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
