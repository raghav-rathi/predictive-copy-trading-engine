# Bollinger on RSI — Calibration

**Shipped:** 20-period 2σ bands on RSI(14), enter on band re-entry,
exit at midline, 1.5xATR stop, no trail, 48-bar max hold.

**What the numbers say:** 47.4% win rate, −$13,075 combined,
expectancy −$17.60/trade — the batch's worst per-trade number. The
midline exit caps winners at the mean while losers run to the stop:
a negative-skew machine. Uniformly bad across coins, so this is not
a regime problem.

**Next experiment (only if revisited):** asymmetric exits — trail the
reversion instead of exiting at the midline, and require a
confirmation close in the trade direction on the entry bar. The entry
logic (exhaustion tag + re-entry) is the sound half; the exit logic
is what kills it.

**Do not:** widen the bands to "be more selective" — fewer trades of
the same negative-skew shape.
