# Cyber Cycle — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Smoothing | smooth = (c + 2c1 + 2c2 + c3) / 6 | Ehlers' published smoother (ch. 4). |
| Cycle alpha | 0.07 | Spec (Ehlers). |
| Signal alpha2 | 0.1 | Spec (Ehlers). |
| Entry | Signal crosses above/below its 1-bar-delayed value | Spec. |
| Exit | Reverse cross | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No spec corrections, no bug fixes requiring re-runs, no PnL-selected
tuning. Implementation note: the cycle recursion starts at bar 5,
once smooth[i], smooth[i-1] and smooth[i-2] are all defined; seeding
earlier with zero-filled lags contaminated the first bars with a
spurious transient (caught by the flat-series unit test).

No bug fixes requiring re-runs, no PnL-selected tuning.
