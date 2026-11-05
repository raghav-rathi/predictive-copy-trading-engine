# Donchian Channel — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Channel length | 20 bars | Published Donchian default. |
| Exit | Close back through midline | Published Donchian exit. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 30 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
