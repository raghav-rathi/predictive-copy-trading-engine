# CCI Extreme — Calibration

All parameters were fixed **a priori** from Lambert's
published CCI specification and 1h-bar reasoning — there is no
in-sample sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| CCI window | 20 | Lambert's standard — the canonical CCI lookback |
| Scale | 0.015 | Lambert's constant — scales CCI so ~70–80% of readings fall inside ±100 |
| Entry levels | ±100 | Lambert's canonical extreme boundaries; the trade is the return through the level, not the touch |
| Exit level | 0 | the mean-reversion target: a stretch that has returned to its average has done its job |
| ATR window | 14 | canonical |
| Stop | 2.0×ATR | standard for a stretch entry (the extreme can extend before it releases) |
| Trail | 2.5×ATR chandelier | locks in the legs that do extend |
| Max hold | 96 bars (~4 days) | a stretch that hasn't snapped back in 4 days is a new regime, not a stretch |
| Risk | 1% / trade, 3× leverage cap | house standard |

The entry rule (cross back through the level, not the touch)
is the whole design: buying while CCI is still falling through
−100 catches the falling knife, and the cross is what confirms
the stretch is releasing (unit-tested — a path that sits below
−100 without crossing never fires). Exits deliberately carry
no level filter: the zero cross is the mean-reversion target
itself.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — a sweep here
would be pure overfitting (872 trades, three coins, one
7-month window).
