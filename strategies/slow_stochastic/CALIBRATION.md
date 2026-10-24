# Slow Stochastic — Calibration

All parameters were fixed **a priori** from Lane's published
stochastic specification and 1h-bar reasoning — there is no
in-sample sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| %K window | 14 | Lane's standard — 14 bars of range is the canonical stochastic lookback |
| %D smoothing | SMA 3 | the "slow" in Slow Stochastic: a 3-bar average of %K is what Lane traded (vs the raw %K of the fast version) |
| Zones | 20 / 80 | Lane's canonical oversold/overbought boundaries |
| ATR window | 14 | canonical |
| Stop | 1.5×ATR | standard for a mean-reversion-prone turn entry (the oscillator whipsaws in chop) |
| Trail | 2×ATR chandelier | locks in the legs that do extend |
| Max hold | 72 bars (~3 days) | a stochastic turn that hasn't resolved in 3 days was noise, not a turn |
| Risk | 1% / trade, 3× leverage cap | house standard |

The entry pair (cross + still-in-zone) is the whole design: a
bare %K/%D cross fires constantly in chop, and the zone filter
is what demands the turn happen off a genuine extreme
(unit-tested — a mid-range cross at %K = 50 is blocked).
Exits deliberately carry no zone filter.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — a sweep here
would be pure overfitting (940 trades, three coins, one
7-month window).
