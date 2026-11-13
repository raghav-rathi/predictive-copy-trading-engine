# RSI Hidden Divergence — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| RSI window | 14 | Wilder's published RSI default. |
| Swing pivot | 5-bar (2 bars each side) | Per spec: the smallest centred pivot that is not a single-bar spike; the standard 5-bar swing definition. |
| Pivot comparison | Strict on the left (past) bars, non-strict on the right (future) bars | Prevents equal neighbouring extremes from double-counting as two pivots. |
| Divergence comparison | Consecutive swing pivots only | Canonical hidden-divergence definition compares the latest pivot against the previous one. |
| Exit level | RSI 50 | Per spec: the RSI midline is where momentum flips sides; crossing it against the position ends the continuation thesis. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 100 | RSI(14) needs 14 bars, but a divergence needs two pivots plus confirmation; 100 bars gives the pivot history time to form. |

## Spec deviations

1. **Two-bar confirmation lag.** A centred 5-bar pivot at bar i
   needs bars i+1 and i+2 to confirm, so the entry fires on bar i+2
   rather than on the pivot bar itself. This is the only causal way
   to trade a centred pivot; the alternative (acting on the pivot bar
   with unconfirmed data) would be lookahead. The lag is the price of
   the definition and is not tuned.
2. **Harness stop/trail as the practical exit.** The system exits on
   the RSI-50 cross alone in the spec. The batch-standard risk layer
   (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on top,
   per the spec's own instruction; 280 of 497 trades ended on the
   stop/trail and 217 on the RSI-50 cross, so both exits genuinely
   contribute here.
3. **No RSI-level filter on the divergence.** Some versions of the
   setup require the RSI pivot low to sit in a particular zone (e.g.
   below 40 for bullish hidden divergence). The spec states no such
   filter, so none was added.

No bug fixes requiring re-runs, no PnL-selected tuning.
