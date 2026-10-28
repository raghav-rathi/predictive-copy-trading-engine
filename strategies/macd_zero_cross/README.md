# MACD Zero Cross

## Mechanism

The MACD line (EMA(12) − EMA(26)) is a trend gauge in its own right: above zero the fast EMA leads the slow EMA and the trend is up; below zero it is down. This strategy trades the zero-line cross itself — the oldest MACD rule in Appel's original formulation — rather than the faster, whipsaw-prone signal-line cross. The signal line and histogram are computed and stored for context but do not gate entries.

## Entry / exit rules

- **Long entry:** MACD line crosses above 0.
- **Short entry:** MACD line crosses below 0.
- **Long exit:** MACD line crosses back below 0 (the opposite cross).
- **Short exit:** MACD line crosses back above 0.

Signals execute at the next bar's open; one position at a time per coin.

## Risk

2xATR stop, 2.5xATR chandelier trail, no fixed target, 168-bar (7-day) max hold, 1% risk/trade, 3x leverage cap.

## Source

MACD (Gerald Appel; StockCharts ChartSchool) — https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/moving-average-convergence-divergence-macd

## Honest caveats

- The zero cross is slow: it confirms a trend only after the fast EMA has already overtaken the slow one, so entries routinely chase moves that are partway done.
- In range-bound chop the MACD oscillates around zero and the strategy whipsaws — this window's BTC/ETH legs show exactly that (win rates ~31–32%, profit factors below 1).
- The HYPE leg is green but thin (+$760 on 174 trades, PF 1.09); that is noise-level, not an edge.
- Single 7-month crypto window; funding unmodeled; next-bar-open execution vs idealized entry.
