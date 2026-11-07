# RSI(2) System — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| RSI period | 2 (Wilder) | Spec (Connors). |
| Trend filter | SMA(200) on 1h closes | Spec (Connors). |
| Long trigger | Close > SMA(200) AND RSI(2) <= 5 | Spec (Connors). |
| Short trigger | Close < SMA(200) AND RSI(2) >= 95 | Spec (Connors). |
| Exit long | Close > SMA(5) | Spec (Connors). |
| Exit short | Close < SMA(5) | Spec (Connors). |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 250 | SMA(200) warmup + margin. |

No spec corrections, no bug fixes requiring re-runs, no PnL-selected
tuning.
