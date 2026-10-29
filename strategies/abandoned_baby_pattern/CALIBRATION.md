# Abandoned Baby Pattern — Calibration

All parameters fixed a priori from Nison's pattern
definition. No in-sample sweep, nothing selected on the
backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| Doji | body <= 10% of range | a true doji: open essentially equals close |
| Long body | body >= 40% of range | first and third candles must be decisive, not spinning tops |
| Gaps | strict, no overlap | the defining feature: doji high < prior low (bullish) and third low > doji high; any overlap demotes it to a doji star |
| Confirmation | close past first candle's midpoint + third-bar volume >= prior 20-bar average | the reversal must reclaim ground and be backed by participation |
| ATR window | 14 | canonical |
| Stop / trail / target | 1.5xATR / 2xATR / 2.5xATR | invalidation sits just beyond the doji extreme; reversals should pay quickly or not at all |
| Max hold | 120 bars (~5 days) | a reversal that hasn't moved in five days was not a reversal |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the gap rule dominates everything else —
with zero qualifying gap-doji sequences on BTC/ETH and one
on HYPE, no other parameter matters in this window. The only
way to get frequency would be to drop the gap requirement,
which changes the pattern's identity; that trade was not
made here.

**Verdict: no-trade (untradeable as specified).** 0 trades on
all three coins. Not a win, not a loss — the setup does not
occur on continuous 1h crypto. Do not trade this as shipped.
