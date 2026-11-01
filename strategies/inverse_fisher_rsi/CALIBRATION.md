# Inverse Fisher RSI — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| RSI period | 5 | Spec. Ehlers' published IFish-RSI length. |
| Scale | 0.1*(RSI-50) | Spec. Ehlers' published scaling. |
| Smoothing | 9-bar WMA | Spec. Ehlers' published smoothing. |
| Thresholds | +/-0.5 | Spec. The strong-zone boundaries. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 20 | 13 bars for RSI(5) + WMA(9) + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
