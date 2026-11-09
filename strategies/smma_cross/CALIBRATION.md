# SMMA Crossover — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Fast SMMA | 9 | Spec. |
| Slow SMMA | 21 | Spec. |
| SMMA seed | SMA of first n closes | Wilder's definition. |
| SMMA recursion | (SMMA_prev × (n−1) + close) / n | Wilder's smoothing, alpha = 1/n. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 50 | Indicator warmup (slow SMMA seed + margin). |

No spec corrections were needed: the SMMA(9)/SMMA(21) cross rules
and the opposite-cross exits are implementable exactly as specified
on 24/7 crypto data (no session gaps involved). The SMMA math was
verified against a hand-recomputed Wilder recursion on a random
walk, and flat data returns the flat price from the seed bar onward.

No bug fixes requiring re-runs, no PnL-selected tuning.
