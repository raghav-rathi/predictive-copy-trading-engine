# Gann Fan — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Anchor window | 30 bars | Spec. Rolling swing window for the fan anchors. |
| Fan slope | 1 x ATR(14) per bar | Spec. The 1x1 angle, volatility-scaled via ATR. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 44 | 30 bars for the swing anchor + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
