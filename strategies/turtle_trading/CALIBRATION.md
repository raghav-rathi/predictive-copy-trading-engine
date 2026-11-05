# Turtle Trading — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Entry channels | 20-bar (System 1) / 55-bar (System 2) | Published Turtle rules. |
| Exit channel | 10-bar (System 1); 20-bar (System 2, subsumed by the tighter 10-bar exit) | Published Turtle rules. |
| N | ATR(20) | Published Turtle rules. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 60 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
