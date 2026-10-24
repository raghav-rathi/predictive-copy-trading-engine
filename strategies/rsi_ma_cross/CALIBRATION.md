# RSI MA Cross — Calibration

All parameters were fixed **a priori** from the published RSI
literature and 1h-bar reasoning — there is no in-sample sweep, so
there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| RSI length | 14 | Wilder's canonical length, and the StockCharts definition the library's shared `base.rsi` implements |
| Signal line | SMA(14) | same length as the RSI itself — the classic "RSI vs its moving average" pairing; a shorter average would track the RSI too closely and fire on noise, a longer one would lag the cross past the move |
| ATR window | 14 | canonical |
| Stop | 1.5×ATR | house standard for a fast momentum entry |
| Trail | 2×ATR chandelier | locks in the momentum legs that do extend |
| Max hold | 72 bars (~3 days) | an RSI cross that hasn't resolved in 3 days was noise, not a momentum handoff |
| Risk | 1% / trade, 3× leverage cap | house standard |

The design bet is that the cross, not the level, carries the
signal — so no overbought/oversold gate is applied. That is a
deliberate, falsifiable choice, and BACKTEST.md is the falsifier.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers — a sweep here would be
pure overfitting (2,744 trades, three coins, one 7-month window).
