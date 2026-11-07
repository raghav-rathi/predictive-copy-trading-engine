# Bollinger Band Squeeze Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Bollinger Bands | 20 bars, 2 std | Standard Bollinger parameters from the source. |
| Squeeze | BandWidth in lowest 15% of last 50 bars | Spec. |
| Squeeze rank window | 50 bars, min_periods=20 (flag defined once 20 non-NaN bandwidth values exist; WARMUP=100 covers the ramp) | Implementation detail: pandas rolling rank needs min_periods non-NaN values before it returns a rank. |
| Squeeze arm window | 10 bars after a squeeze | Spec interpretation: entry only after a squeeze; the arm window lets the breakout fire as bands start expanding. |
| Entry | Close crosses outside the band while armed | Spec (cross, so one entry per breakout). |
| Exit | Close back inside the bands | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No spec corrections, no bug fixes requiring re-runs, no PnL-selected tuning.
