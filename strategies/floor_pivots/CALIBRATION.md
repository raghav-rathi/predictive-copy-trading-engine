# Floor-Trader Pivots — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Session window | 24 completed 1h bars | Spec: one "session" on 1h data. |
| Pivot formulas | PP=(H+L+C)/3, R1=2PP−L, S1=2PP−H, R2=PP+(H−L), S2=PP−(H−L) | Classic floor-trader pivots (source). |
| Volume filter | Volume above 20-bar average | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No spec corrections were needed: the levels, bias, entry, and exit
rules are all implementable exactly as specified on 24/7 crypto data
(no session gaps involved).

No bug fixes requiring re-runs, no PnL-selected tuning.
