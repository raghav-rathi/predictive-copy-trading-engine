# Kicker Pattern — Calibration

All parameters fixed a priori from the Nison kicking
definition. No in-sample sweep, nothing selected on the
backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| Gap test | o2 > o1 (bullish) / o2 < o1 (bearish) | Nison's kicking definition: the second open must clear the first candle's open, not just its close |
| Second-body strength | body >= 0.5 * range | a kicker candle must be decisive, not a doji-like sliver |
| Trend filter | none | the kicking reference treats the preceding trend as of little importance; the gap is the surprise |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for a gap reversal to follow through |
| Target | none | the opposite-kicker exit manages the trade |
| Max hold | 72 bars (~3 days) | a gap reversal that has not followed through in three days was noise |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the gap test is the whole pattern. On 1h
crypto it is extremely strict (5 signals in ~16,350 bars)
because opens track prior closes, so clearing the prior open
after an opposite-color candle means clearing that candle's
entire body. Relaxing it to o2 > c1 would no longer be a
kicker — it would be any reversal candle — and was not tested
here. The body-strength threshold (0.5) barely binds: the gap
test does almost all the filtering.

**Verdict: loser on a trivial sample.** -$76 combined over 5
trades (1 win). Do not trade this as shipped; the sample is
too small to support any stronger claim in either direction.
