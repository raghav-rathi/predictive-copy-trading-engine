# Wyckoff Upthrust — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Range window | 20 prior bars | Spec. 20 bars ≈ 20 hours of range context; prior bars only, so the breakout bar is judged against a range it did not form. |
| Upthrust rule | h > range_high AND range_low < c < range_high | Spec. The literal failed-breakout definition: break above, close back inside. |
| Short exit | Close crosses above range_high | Spec. Reclaim above the range invalidates the failed-breakout thesis. |
| Sides | Short only | Spec. The upthrust is a distribution/bearish event; its mirror (spring) is a separate strategy. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 25 | Spec minimum: 20 bars for the range + shift, +5 margin. |

No bug fixes requiring re-runs, no PnL-selected tuning. The negative
backtest (BACKTEST.md) was not tuned upward.
