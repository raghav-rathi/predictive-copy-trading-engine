# MACD Bollinger — Calibration

All parameters fixed a priori from the textbook MACD and
Bollinger constructions. No in-sample sweep, nothing selected
on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| MACD fast / slow / signal | 12 / 26 / 9 | canonical Appel parameters |
| Bands on MACD line | SMA(20), +/-2 SD | canonical Bollinger parameters, applied to the MACD line per the Carter setup |
| Zero-side filter | long only with MACD < 0, short only with MACD > 0 | the entry must be an oversold/overbought release, not a mid-trend wobble |
| Exit | cross of band midline or signal line, adverse direction | the release has run back to the mean; no fixed target |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for a release to develop |
| Max hold | 168 bars (~7 days) | a release that hasn't mean-reverted in a week was not a release |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the zero-side filter is doing real work —
without it the lower-band cross fires on every mid-trend dip
of a strong uptrend. The remaining failure mode is structural,
not parametric: on 1h crypto the MACD line re-entering its
band is as often a continuation pause as a turn, and no band
width in the plausible range changes that story. Widening the
bands would cut trades but would also delay the release signal
past the move it is meant to catch.

**Verdict: loser.** -$5,711 combined over 417 trades, red on
all three coins. Do not trade this as shipped.
