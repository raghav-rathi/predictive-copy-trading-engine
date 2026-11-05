# Elder Impulse System — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| EMA / MACD histogram | 13 / (12,26,9) | Elder's published Impulse System defaults. |
| Entry / exit triggers | First bar of a new impulse colour; exit on any non-entry colour | Published mechanism: trade the impulse colour change. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 40 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
