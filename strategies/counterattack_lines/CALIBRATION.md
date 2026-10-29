# Counterattack Lines — Calibration

All parameters fixed a priori from the Nison counterattack
definition. No in-sample sweep, nothing selected on the
backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| Trend filter | 5 bars, in the pre-pattern direction | the pattern is defined as occurring after a trend |
| Gap at the open | o2 < c1 (bullish) / o2 > c1 (bearish) | the second session gaps against the trend, then fights back |
| Close tolerance | \|c2 - c1\| <= 0.2 * ATR(14) | "same close" in Nison's terms, scaled to volatility instead of a fixed price distance |
| Body-size similarity | ratio within 2/3–3/2 | "similar size" candles; a tiny second candle is not a counterattack, it is noise |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for a bridled trend to turn |
| Target | none | the opposite-counterattack exit manages the trade |
| Max hold | 72 bars (~3 days) | a bridled trend that has not turned in three days was just a pause |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the close tolerance is the binding
parameter. At 0.2xATR it is tight (a few dollars on BTC 1h);
widening it would admit piercing-style candles that push
past the prior close, which is a different, stronger pattern
— and would also admit ordinary two-candle noise. The
body-ratio band (2/3–3/2) is the second filter: without it,
doji-like second candles that happen to close near the prior
close would flood the signal. Neither was widened here: the
losing result is reported as-is, consistent with Nison's own
"weaker than piercing" ranking.

**Verdict: loser.** -$940 combined over 27 trades (PF 0.41),
BTC 0-for-8. Do not trade this as shipped.
