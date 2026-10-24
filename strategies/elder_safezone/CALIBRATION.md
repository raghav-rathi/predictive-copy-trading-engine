# Elder SafeZone — Calibration

All parameters were fixed **a priori** from Elder's published
SafeZone specification and 1h-bar reasoning — there is no
in-sample sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Trend EMA | 22 | Elder's trend filter; ~1 day of 1h bars, the standard intermediate-trend length |
| SafeZone window | 10 | Elder's published lookback — long enough to sample real pullback depth, short enough to adapt when volatility shifts |
| Penetration multiple | 2.5 | Elder's published default — the line sits 2.5 average penetrations beyond the extreme, so only an abnormally deep counter-trend bar breaks it |
| ATR window | 14 | canonical |
| Stop | 2.0×ATR | catastrophe backstop behind the SafeZone line (the line itself is the primary exit) |
| Trail | 2.5×ATR chandelier | locks in the trend legs that extend past the line |
| Max hold | 96 bars (~4 days) | a trend trade that hasn't resolved in four days is chop, not trend |
| Risk | 1% / trade, 3× leverage cap | house standard |

The entry pair (EMA cross + still-above-the-line) is the whole
design: the cross alone fires on every EMA whipsaw, and the
SafeZone condition is what demands the trend be intact at the
moment of entry (unit-tested — a cross below the line is
blocked). Exits deliberately carry no EMA condition: the line
is the arbiter once the trade is on.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — a sweep here
would be pure overfitting (1,202 trades, three coins, one
7-month window).
