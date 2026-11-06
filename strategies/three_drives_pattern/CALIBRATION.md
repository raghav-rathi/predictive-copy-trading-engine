# Three Drives Pattern — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Zigzag pivots | 5-bar local extrema, min swing 0.9x ATR(14), confirmed 2 bars late | Spec: swing detector shared across batch 28 geometric strategies. |
| Retracements | 0.618 / 0.786 (±0.08) | Published Three Drives ratios. |
| Extensions | 1.272 / 1.618 (±0.10) | Published Three Drives ratios. |
| Drive symmetry | each drive length within 0.5x–2x of the first | Spec. |
| Entry window | 10 bars after D3 completes, reversal bar only | Spec. |
| Exit | 61.8% retracement of the full move from D3 | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
