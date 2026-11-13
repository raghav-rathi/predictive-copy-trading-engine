# Smash Day — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Wide-day multiple | 1.5x the 20-day mean daily range | Williams' published Smash Day definition (a wide-range day preceding the inside day). |
| Mean-range window | 20 days | Williams' published lookback for the range comparison. |
| Inside-day definition | High < prior high AND low > prior low | The textbook inside-day definition. |
| Setup validity | 2 days after the inside day | Williams trades the next day; the second day is allowed a priori because a 1h-bar break can arrive late on 24/7 crypto. Fixed before running, not tuned. |
| Entry | 1h close crossing the inside day's high/low | The breakout of the contraction range, read on hourly closes. |
| Exit | Opposite break, plus harness stop/trail | Per spec: a failed break is the exit signal. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 1200 | Needs ~50 days of daily context (20-day mean range + inside/wide sequencing); 1200 hourly bars ≈ 50 days. |

## Spec deviations

1. **UTC calendar days instead of session days.** Williams' system is
   written on daily bars anchored to the equity session. Crypto trades
   24/7, so the day is the UTC calendar day; the accumulation window is
   the whole day, not a session slice.
2. **Two-day validity instead of one.** Williams trades the break on
   the day immediately after the inside day. The shipped version allows
   the following day too, fixed a priori — the break of a daily range
   read on 1h bars can print late, and the window was chosen before
   any backtest was run.
3. **Harness stop/trail as the practical exit.** Williams' system exits
   on the opposite break (or a time stop). The batch-standard risk
   layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on
   top, per the spec's own instruction; in practice all 39 trades
   ended on the stop, so the shipped result is entry + stop/trail.

No bug fixes requiring re-runs, no PnL-selected tuning.
