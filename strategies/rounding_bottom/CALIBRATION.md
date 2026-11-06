# Rounding Bottom — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Window | 60 bars | Spec. |
| Trough position | Middle third of window (positions 20–39) | Spec. |
| Rims | Max close first 15 bars / last 15 bars, within 2% | Spec. |
| Trough depth | >= 3x ATR(14) below the lower rim | Spec. |
| U-shape | 10-bar SMA slope negative first half, positive second half | Spec. |
| Volume confirmation | Volume > SMA20(volume) | Spec. |
| Entry / exit recency | Within 20 bars of detection / exit within 120 bars | Spec (re-arm window; exit horizon matches max hold). |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 70 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
