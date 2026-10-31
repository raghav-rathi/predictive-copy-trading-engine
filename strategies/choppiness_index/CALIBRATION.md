# Choppiness Index — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| CHOP period | 14 | Spec; the Dreiss default, also the source's standard lookback. |
| Trending threshold | 38.2 | Spec; the source's Fibonacci trending level (below = trending). |
| Choppy threshold | 61.8 | Spec; the source's Fibonacci choppy level (above = consolidating). |
| Donchian period | 20 | Spec; the classic Donchian channel length, prior-bar only for causality. |
| Zero-range guard | NaN | Spec; a flat window has no defined CHOP, so no signal is emitted. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 30 | Spec minimum: 21 bars for prior-bar Donchian(20), 14 for CHOP/ATR, +9 margin. |

No bug fixes requiring re-runs, no PnL-selected tuning. The losing
backtest (BACKTEST.md) was not tuned upward.
