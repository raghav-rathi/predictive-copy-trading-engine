# Megaphone Pattern — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Swing pivots | 5-bar local extrema, usable 2 bars after the extreme | Spec: no-lookahead pivot confirmation. |
| Pattern | 3 higher highs + 3 lower lows, alternating | Edwards & Magee broadening formation. |
| Expansion threshold | >= 0.5x ATR(14) per swing | Spec: expanding range, diverging boundaries. |
| ATR window | 14 | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
