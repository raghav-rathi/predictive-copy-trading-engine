# Supertrend RSI — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Supertrend | (10, 3.0) | The spec's parameters; standard Supertrend (Wilder ATR(10), 3x multiplier) via the shared `strategies.base.supertrend` helper. |
| RSI | 14 (Wilder) | The spec's parameter, via the shared `strategies.base.rsi` helper. |
| RSI trigger | Cross of 50 | The spec's entry trigger; a genuine cross (previous RSI on the old side, current RSI on the new side), not a level. |
| Price-vs-line test | Close vs the Supertrend line | "Price above/below the Supertrend line" read as the close vs the shipped line (lower band in an uptrend, upper band in a downtrend). |
| Exit | Supertrend direction flip (+1 -> -1 for longs, -1 -> +1 for shorts) | The spec's exit: the flip is the close falling below / rising above the line, implemented on the direction column rather than a raw close-vs-line cross (the line jumps to the opposite band on the flip bar, so a raw cross against the post-flip line would miss the flip). |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Supertrend needs 10 bars of ATR + band seeding; RSI(14) needs 14 bars; 60 covers both with margin. |

## Spec deviations

1. **Exit on the direction flip, not a close-vs-line cross.**
   The spec says "Supertrend flips bearish (price closes below
   the line)". The flip happens exactly when the close crosses
   the opposing band; on the flip bar the line itself jumps to
   the other band, so comparing the close to the post-flip line
   would not detect the event. The shipped exit compares the
   direction column (+1 -> -1), which is the same event stated
   without the line-jump artifact.
2. **RSI cross is a genuine cross.** "RSI crosses above 50"
   requires the previous bar's RSI at or below 50 and the
   current bar's above 50 (via `base.crossed_above`). RSI merely
   sitting above 50 does not re-enter.
3. **Harness stop/trail as an additional exit.** The spec's exit
   is the Supertrend flip; the batch-standard risk layer (2xATR
   stop, 2.5xATR trail, 120-bar max hold) is applied on top, per
   the batch instruction. Only 36 of 488 trades ended on the
   flip, so the reported result is mostly entry + harness.
4. **Shared helpers reused, not reimplemented.** Supertrend,
   RSI, and ATR all come from `strategies.base` (the same code
   the template's sibling strategies use); no local copies.

No bug fixes requiring re-runs, no PnL-selected tuning.
