# Wolfe Wave — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Zigzag pivots | 5-bar local extrema, min swing 0.9x ATR(14), confirmed 2 bars late | Spec: swing detector shared across batch 28 geometric strategies. |
| Convergence | 1-3 and 2-4 lines intersect ahead of point 5 (within 300 bars) | Published Wolfe Wave definition. |
| Entry window | 20 bars after point 5 completes | Spec. |
| Exit | EPA line through points 1 and 4 | Published Wolfe Wave definition. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
