# MACD Histogram Reversal — Calibration

All parameters fixed a priori from the Elder histogram
construction and the canonical MACD parameters. No in-sample
sweep, nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| MACD fast / slow / signal | 12 / 26 / 9 | canonical Appel parameters; the histogram is macd − signal |
| Flip definition | first uptick after a decline (trough) / first downtick after a rise (peak), using hist[i-2..i] only | Elder's slope-flip rule, kept strictly causal |
| Sign filter | trough flip counts only with hist < 0, peak flip only with hist > 0 | the turn must come from the appropriate side of zero, not from chasing an already-extended run |
| Exit | opposite flip, or a zero cross in the adverse direction | the flip thesis is spent once momentum reverses again or gives back the whole move |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2xATR | tight trail, matching the fast nature of a flip signal |
| Max hold | 72 bars (~3 days) | a flip that hasn't paid in three days was noise |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the failure is not a parameter problem, it
is a frequency problem — 1,844 trades means the histogram's
local slope flips on a large fraction of all bars, and the
sign filter only halves that. Any fix would have to change
the signal definition itself (e.g. flips only at histogram
extremes, or flips confirmed by the MACD line crossing its
signal), which is a different strategy, not a calibration
tweak — and it was not tested here and must not be fitted to
this window.

**Verdict: loser.** -$18,600 combined over 1,844 trades,
worst in this batch, max drawdowns -56% to -68%. Do not trade
this as shipped.
