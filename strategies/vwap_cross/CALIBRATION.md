# Rolling VWAP Cross — Calibration

All parameters were fixed **a priori** from the published VWAP
literature and 1h-bar reasoning — there is no in-sample sweep, so
there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| VWAP window | 24 | 1 day of 1h bars — the natural session-less stand-in for the classic session-anchored VWAP |
| Slope lookback | 3 | ~3 hours is enough for the 24-bar benchmark to tilt; shorter is noise, longer delays the filter |
| Volume filter | 1.2× | VWAP is the institutional benchmark — the cross must print on above-average flow or it carries no institutional signal |
| ATR window | 14 | canonical |
| Stop | 1.5×ATR | standard for a mean-reversion-prone entry (the benchmark pulls price back) |
| Trail | 2×ATR chandelier | locks in the momentum legs that do extend |
| Max hold | 72 bars (~3 days) | a momentum handoff that hasn't resolved in 3 days was noise, not a handoff |
| Risk | 1% / trade, 3× leverage cap | house standard |

The entry triple (cross + slope + volume) is the whole design:
a bare VWAP cross whipsaws in chop (unit-tested — a cross
against a flat VWAP is blocked, a cross on 0.5× volume is
blocked), so the filters exist to demand a *trend-consistent,
flow-backed* cross. Exits deliberately carry no filters.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers — a sweep here would be
pure overfitting (226 trades, three coins, one 7-month window).
