# EMA Ribbon — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| EMA periods | 8, 13, 21, 34, 55 | Spec: Fibonacci ribbon. |
| Expansion threshold | spread > 0.002 (long), < −0.002 (short) | Spec. |
| Entry trigger | First bar of full alignment (not aligned prior bar) | Spec. |
| Exit | Alignment break (ema8 vs ema21) or close vs ema34 | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No spec corrections were needed: the five-EMA ribbon, the
first-alignment trigger, the 0.002 spread expansion filter, and the
alignment-break / EMA34 exits are all implementable exactly as
specified on 24/7 crypto data (no session gaps involved). Note: on the
very first bar with valid EMAs there is no previous bar, so it counts
as a first alignment by construction (previous alignment treated as
false) — this only affects the first bar of the series, not live
trading.

No bug fixes requiring re-runs, no PnL-selected tuning.
