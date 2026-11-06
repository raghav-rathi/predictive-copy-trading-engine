# Shooting Star Pattern — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Trend context | EMA(20), 5-bar return +/-1% | Standard Nison trend context. |
| Body limit | <= 30% of range | Small-body requirement for a star/hammer. |
| Body position | Within lower / upper 35% of range | Body at the trend-opposite end of the bar. |
| Long shadow | >= 2x body | Classic shooting-star / hammer shadow rule. |
| Short shadow | <= 10% of range | Negligible shadow on the other side. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 30 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
