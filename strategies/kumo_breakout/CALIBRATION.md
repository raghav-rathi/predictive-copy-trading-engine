# Kumo Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Tenkan / Kijun / Senkou | 9 / 26 / 52 | Spec. Standard Ichimoku periods. |
| Cloud shift | 26 bars | Spec. The cloud is plotted 26 bars forward. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 90 | 52 bars for Senkou B + 26-bar shift + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
