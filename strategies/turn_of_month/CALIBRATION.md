# Turn of the Month — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Entry bar | 00:00 UTC bar of the last calendar day | The spec's "first bar of the last calendar day of each month (00:00 UTC bar)". |
| Exit bar | 23:00 UTC bar of the 3rd calendar day of the next month | The spec's "23:00 UTC bar of the 3rd calendar day of the next month". |
| Holding window | ~4 days fill-to-fill (entry fills 01:00 last day, exit fills 00:00 day 4) | Follows from the entry/exit bars plus the harness next-bar-open execution; documented in the README, not chosen. |
| Shorts | none (`allow_shorts=False`) | The spec's "No shorts: allow_shorts=False". |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer; max hold 120 covers the ~95-bar fill-to-fill window with margin. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Per the spec; the strategy needs no indicator warmup (calendar only), 60 is margin. |

## Spec decisions / ambiguities

1. **The window was not widened.** The spec's window yields
   exactly 8 trades per coin (month-ends Mar 31–Oct 31 inside
   the backtest window; the Nov 30 turn falls outside it).
   Selective is fine and honest; no extra days were added to
   manufacture trades.
2. **Missing bars manufacture nothing.** If the 00:00 bar of
   the last day or the 23:00 bar of day 3 is absent from the
   data, that leg simply does not fire (verified by
   `test_missing_entry_bar_means_no_entry`). The harness max
   hold bounds the position if the exit bar is missing.
3. **Date logic from the bar timestamp only.** `t` is converted
   with `pd.to_datetime(t, unit="ms", utc=True)`; no wall-clock
   time is read anywhere. `days_in_month` handles 28/29/30/31
   correctly (February 2026 = 28 days; leap-year handling comes
   free from pandas).
4. **The calendar exit never fired.** All 24 shipped trades
   ended on the harness stop/trail before the day-3 exit bar.
   This is a property of the 2xATR stop / 2.5xATR trail over a
   ~4-day 1h hold in crypto, reported as found — not a reason
   to loosen the risk layer (that would be tuning to PnL).
5. **No bug fixes requiring re-runs, no PnL-selected tuning.**

## What the exits actually did

Shipped run (24 trades): 24 exits on the harness stop/trail, 0
on the signal exit. The signal exit is correctly defined (the
unit tests pin it to the exact bars), but no position survived
long enough to reach it.
