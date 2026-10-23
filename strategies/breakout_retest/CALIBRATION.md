# Breakout-Retest Throwback — Calibration

All parameters were fixed a priori from the canonical
breakout-retest literature and the task spec: 20-bar range,
20-bar retest window, 0.1/0.5 ATR touch/loss bands, ATR(14),
1.0×ATR stop, 2.0×ATR target, 96-bar max hold. **No parameter
was fitted on the backtest window, and no sensitivity sweep was
run on it — a sweep on this window would be in-sample selection,
which this file refuses to do.** The shipped configuration is
the a-priori one, full stop.

The only calibration content here is what the backtest itself
reveals about the *mechanism* at these settings (see
BACKTEST.md): at the canonical 1.0×ATR stop / 2.0×ATR target, the
system needs a >33% win rate to break even before costs. It
delivers 30–33% with 0.055%/side costs, and ~64% of trades die
on the hard stop. Any "recalibration" (wider stop, deeper touch
band, longer window, time-of-day filters) must be designed on
walk-forward data, not on the 2026-03-14 → 2026-10-23 window —
that would be fitting to the noise that produced the −$8,578.
