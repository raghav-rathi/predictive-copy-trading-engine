# Chaikin ADL Trend — Calibration

All parameters were fixed **a priori** from the published Chaikin
literature and 1h-bar reasoning — there is no in-sample sweep, so
there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| ADL signal line | SMA(10) | Chaikin's standard short signal average for the ADL; long enough to smooth single-bar money-flow spikes, short enough to turn with accumulation shifts |
| Trend filter | SMA(50) | ~2 days of 1h bars — the medium-term trend the cross must agree with; shorter lets chop through, longer delays the filter past the move |
| ATR window | 14 | canonical |
| Stop | 1.5×ATR | house standard for a momentum-handoff entry |
| Trail | 2×ATR chandelier | locks in the accumulation legs that do extend |
| Max hold | 72 bars (~3 days) | an ADL cross that hasn't resolved in 3 days was noise, not a money-flow handoff |
| Risk | 1% / trade, 3× leverage cap | house standard |

The design bet is that the SMA(50) filter rescues the ADL cross
from chop: accumulation that disagrees with the 50-bar trend is
treated as a flicker, not a signal. Exits deliberately carry no
filter.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers — a sweep here would be
pure overfitting (1,512 trades, three coins, one 7-month window).
