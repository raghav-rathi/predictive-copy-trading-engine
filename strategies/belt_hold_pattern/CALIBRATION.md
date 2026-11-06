# Belt Hold Pattern — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Trend context | EMA(20), 5 prior bars / 5-bar return ±1% | Spec (Nison trend context). |
| Open-to-extreme | Within 10% of range of the low (bullish) / high (bearish) | Spec. |
| Body | >= 60% of range | Spec. |
| Far-side shadow | <= 15% of range | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 30 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
