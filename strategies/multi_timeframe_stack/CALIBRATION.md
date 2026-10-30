# Multi-Timeframe Stack — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Higher timeframe | 4h (groups of 4 1h bars) | Spec. 4x the entry timeframe, the standard MTF spacing (higher frame ~4–6x the trading frame). |
| 4h trend EMAs | 20 / 50 | Spec. Fast/slow pair on the higher frame; 50 4h bars ≈ 8.3 days of trend context. |
| 1h entry EMAs | 9 / 21 | Spec. Classic fast/slow cross pair on the entry frame. |
| Causality rule | Only completed 4h bars | Spec. A 1h bar uses 4h bars completed before it; the in-progress 4h bar is excluded. Verified by the incomplete-4h-bar test. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 230 | Spec minimum: 4×50 = 200 1h bars for the 4h EMA(50), +21 for the 1h EMA(21), +9 margin. |

No bug fixes requiring re-runs, no PnL-selected tuning. The mildly
positive backtest (BACKTEST.md) is small enough to be noise; it was not
tuned upward.
