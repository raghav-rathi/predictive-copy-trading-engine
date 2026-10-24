# TTM-Style Keltner Squeeze Breakout — Calibration

All parameters were fixed **a priori** from the published TTM
Squeeze construction and 1h-bar reasoning — there is no
in-sample sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Bollinger Bands | 20 / 2.0 | the squeeze's inner band — Carter's construction uses the standard Bollinger setup |
| Keltner Channels | EMA20 ± 1.5 × ATR(10) | the squeeze's outer band — the ATR multiplier is what makes the comparison a volatility statement, not a price statement |
| Squeeze lookback | 3 bars | a breakout must follow compression promptly; 3 bars admits a squeeze that released a bar or two before the breakout print, but rejects stale squeezes |
| ATR window (risk) | 14 | canonical; deliberately different from the KC's ATR(10), which serves the squeeze definition, not the stop |
| Stop | 2.0×ATR | a breakout that retraces less than 2 ATR is still a breakout — the wider stop (vs the 1.5×ATR band-tag stop) is the point |
| Trail | 2.5×ATR chandelier | gives the expansion room to run while locking in the move |
| Max hold | 96 bars (~4 days) | a genuine volatility expansion resolves within days; a breakout stalled for four days was a false release |
| Risk | 1% / trade, 3× leverage cap | house standard |

The design bet is that compression-then-breakout selects for
real moves better than a raw band breakout: the squeeze gate
should cut the false-breakout rate. The backtest (BACKTEST.md)
tests exactly that bet — and on this window it roughly breaks
even in aggregate (+$900 across 408 trades) with one genuinely
good leg (ETH, PF 1.33) and two flat-to-negative legs. That is
a mixed verdict, not an edge — and not a reason to retune the
lookback or the multiplier on this window.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers.
