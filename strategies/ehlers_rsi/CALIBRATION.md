# Ehlers RSI — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| SuperSmoother period | 10 bars | Ehlers' standard short cutoff for the pre-filter; the same 2-pole recursion and coefficients as `strategies/ehlers_supersmoother` (period 20 there, 10 here). |
| SuperSmoother seed | First two values = price | The `ehlers_supersmoother` batch convention; avoids start-up blowup on a price-level filter. |
| RSI period | 14 bars | Wilder's published RSI period, applied to the smoothed series. |
| Oversold / overbought | 30 / 70 | The classic RSI thresholds, per spec. Crosses are strict (previous value ≤ level, current > level, and vice versa). |
| Long entry / short entry | RSI crosses above 30 / below 70 | Per spec. |
| Long exit / short exit | RSI crosses above 70 / below 30 | Per spec. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Covers SuperSmoother(10) settling plus RSI(14) convergence with margin. |

## Spec deviations

None. The implementation follows the spec exactly as written. Note
the deliberate distinction from `adaptive_rsi` (Kaufman-AMA based):
this strategy smooths with Ehlers' SuperSmoother and uses a fixed
Wilder RSI(14).

No bug fixes requiring re-runs, no PnL-selected tuning.
