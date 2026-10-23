# WaveTrend Oscillator — Calibration

All parameters were fixed **a priori** from the canonical
LazyBear release (see README.md sources): n1=10, n2=21, wt2
SMA(4), oversold/overbought ±53, exit extremes ±60. There was no
in-sample selection and there is no parameter sweep in this file.

This is deliberate, and the backtest gives the reason: the shipped
config loses on every coin in the window (combined -$5,656, PF <
1 on all three legs). When the canonical settings fail that
cleanly, running a grid over ±53/±60 or n1/n2 to find something
that backtests green would be textbook overfitting to noise. The
honest next step is walk-forward or out-of-sample work (different
timeframe, rescaled zone lines, wider stops), not a sweep on this
window.

**Shipped decision:** keep the canonical LazyBear parameters
exactly as published. No optimization performed, none attempted.
