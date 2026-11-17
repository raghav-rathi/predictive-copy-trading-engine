# Trendline Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Pivot window | 10 bars (5 each side) | The spec's swing-pivot definition; a strict-greater test on both sides. |
| Pivot confirmation | 5 bars after the pivot bar | A pivot at bar i needs the 5 bars to its right to be known; the shipped `swing_high` / `swing_low` columns are True only on the confirmation bar (i+5), never on the pivot bar itself. |
| Trendline | Straight line through the last two confirmed pivots, extrapolated to the current bar | The spec's Demark-style construction; the line is recomputed causally every bar from the pivots confirmed by that bar. |
| "Breaks" | Cross, not level | A close merely sitting beyond a line is not a break; entry requires the previous close on the old side and the current close on the new side. A cross also cannot fire on the bar a line first appears (previous-bar comparison vs a NaN line is False). |
| Exit | Opposite line break | Per spec: a long exits on a close crossing below the uptrend line, a short on a close crossing above the downtrend line. Note the exit line is a DIFFERENT line from the entry line. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 120 | Two pivots + 5-bar confirmation + margin; the line needs at least two confirmed pivots of a kind before it exists at all. |

## Spec deviations

1. **Confirmation lag implemented honestly.** The spec's note is
   followed literally: a line through two pivots is only valid
   once the second pivot is confirmed (5 bars after it forms).
   The raw centered pivot is computed internally and then shifted
   by 5 bars before anything downstream sees it, so no signal can
   use an unconfirmed pivot. The cost is visible in the backtest:
   by the time a line exists, price has often already moved
   through the level the line was drawn to catch.
2. **Strictly-greater pivots.** A swing high must be strictly
   greater than each of the 5 bars on each side; two adjacent
   equal highs are not pivots (tested). Ties are common on
   low-volatility bars and would otherwise double-count a level.
3. **Cross, not level, for "breaks".** The spec says "close
   breaks above/below the line". Reading that as a level
   (close > line) would re-enter on every bar while price stays
   beyond a line; the cross reading is the standard one and is
   documented here.
4. **Harness stop/trail as an additional exit.** The spec's exit
   is the opposite line break; the batch-standard risk layer
   (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on
   top, per the batch instruction. 709 of 959 trades ended on
   the stop/trail, so the reported result is mostly entry +
   harness, not the pure line-to-line system.

No bug fixes requiring re-runs, no PnL-selected tuning.
