# MACD Histogram Divergence

The Aspray MACD-Histogram divergence: price makes a lower low while
the histogram makes a higher low (bullish), or price makes a higher
high while the histogram makes a lower high (bearish). Divergence is
detected when the second price pivot confirms (5-bar zigzag lag) and
fires exactly once per pivot pair.

## Rules

- Long entry: bullish divergence bar (price lower low, histogram
  higher low).
- Short entry: bearish divergence bar (price higher high, histogram
  lower high).
- Exit: the histogram crosses back through zero AFTER having been
  positive (longs) or negative (shorts) during the position — the
  "seen" guard matters, because a bullish divergence usually fires
  while the histogram is still negative, so a plain "exit when hist
  < 0" rule would exit on the very next bar. Opposite divergence
  also exits.
- Risk: 2xATR stop, 2.5xATR chandelier trail, no fixed target,
  120-bar (5-day) max hold, 1% equity risk per trade, 3x leverage cap

Source: MACD-Histogram divergence (Appel; Aspray, StockCharts
ChartSchool).
