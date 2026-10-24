# Ehlers Instantaneous Trendline — Calibration

All parameters were fixed **a priori** from Ehlers' published
formulation and 1h-bar reasoning — there is no in-sample sweep,
so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Alpha | 0.07 | Ehlers' published Instantaneous Trendline default (Cybernetic Analysis for Stocks and Futures / Cycle Analytics for Traders); the filter's entire lag/smoothness trade-off lives in this one number, and changing it would be tuning |
| Price input | close | the assigned spec; Ehlers' own presentations sometimes use (h+l)/2 — close is the noisier, more conservative choice, and the backtest must be read as testing the close-input variant |
| Seed | IT[0]=P[0], IT[1]=P[1] | seeded with price, per the spec; the WARMUP absorbs the seeding transient |
| ATR window | 14 | canonical |
| Stop | 1.5×ATR | house standard for a fast trend-birth entry |
| Trail | 2×ATR chandelier | locks in the trend legs that do extend |
| Max hold | 72 bars (~3 days) | an IT cross that hasn't resolved in 3 days was noise, not a trend birth |
| Risk | 1% / trade, 3× leverage cap | house standard |

The design bet is that low lag is the edge: a close/IT cross
fires earlier than a close/SMA cross, so it catches trend
births before the lagging-average crowd. BACKTEST.md tests that
bet directly.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers — a sweep here would be
pure overfitting (2,448 trades, three coins, one 7-month window).
