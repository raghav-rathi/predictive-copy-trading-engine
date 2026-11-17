# Triple RSI — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| RSI lookbacks | 7 / 14 / 21 | The spec's three Wilder RSIs: fast, standard, slow. |
| Long threshold | All three > 55 | Per spec; strict greater-than on the entry bar. |
| Short threshold | All three < 45 | Per spec; strict less-than on the entry bar. |
| Entry trigger | First bar all three are on the same side after at least one was not | Per spec: "triggered on the bar the last of the three crosses" — a transition into full agreement, not every aligned bar. |
| Exit threshold | Any RSI crosses 50 | Per spec: long exits when any RSI crosses below 50, short when any crosses above 50. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Slowest RSI(21) needs 21 bars plus Wilder smoothing to settle; 60 gives margin. |

## Spec deviations

1. **"Triggered on the bar the last crosses" = transition into
   full agreement.** The spec's phrasing is implemented as: the
   entry fires on the first bar where all three are beyond the
   threshold and the previous bar had at least one short of it.
   It does not fire again while the alignment persists. The
   alternative (fire on every aligned bar) would re-enter
   immediately after every exit and is not a "trigger".
2. **No entry on bar 0.** There is no previous bar to cross from,
   so a series that starts already aligned produces no entry.
   This matters only for synthetic flat/rising starts, not for the
   backtest (warmup 60).
3. **Exit is a genuine cross, not a level.** "Any RSI crosses
   below 50" requires the RSI to be at/above 50 on the previous
   bar and below 50 on the exit bar; merely sitting below 50 does
   not exit. Same for the short side.
4. **Harness stop/trail as an additional exit.** The batch-standard
   risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is
   applied on top of the spec's exit, per the batch instruction.
   631 of 1294 trades ended on the stop/trail, 663 on the signal
   exit, so both exits matter here.

No bug fixes requiring re-runs, no PnL-selected tuning.
