# POC Migration — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Profile window | 50 bars (~2 days) | Spec. Long enough for a stable profile, short enough to migrate with regime shifts. |
| Bins | 20 | Spec. Finer bins would fragment volume and make the POC jump between adjacent bins on noise; coarser bins would lose level resolution. |
| Bin assignment | Bar's close | Documented simplification: 1h candles carry no tick-level volume-at-price, so the close is the single representative price per bar. |
| POC lag | 10 bars | Spec. Compares the current POC to the POC 10 bars ago to define migration direction. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 65 | 50-bar window + 10-bar lag + 5 margin. |

No bug fixes requiring re-runs, no PnL-selected tuning. The poor
backtest (BACKTEST.md) is reported, not tuned away: shortening the lag
or window to cut the trade count would be fitting to this window.
