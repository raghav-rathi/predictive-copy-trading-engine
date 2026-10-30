# Point & Figure

Classic Point & Figure charting (Dorsey), built causally from 1h closes.

## Mechanism

- **Box size:** 1% of the current price level, recomputed ONLY when a new
  column starts, so boxes are stable within a column. At BTC ~$100k a box
  is ~$1,000; at HYPE ~$20 a box is ~$0.20.
- **Columns:** X columns track rising prices, O columns falling prices.
  A close extends the column; a close at least 3 boxes against the column
  (3-box reversal) starts a new column in the opposite direction.
- **Only closes are used.** Classic P&F is price-only and time-blind; the
  bar's close is the price that extends, flips, or ignores. Intraday
  highs/lows inside a bar do not create boxes.

## Entry / exit

- **Long entry:** double-top breakout — an X column's high exceeds the
  high of the previous X column.
- **Short entry:** double-bottom breakdown — an O column's low goes below
  the low of the previous O column.
- **Exit:** a 3-box reversal in the opposite direction (the column flips).
  The risk layer adds a 2xATR stop, a 2.5xATR chandelier trail, and a
  120-bar (5-day) max hold.

## Source

- Point & Figure charts, StockCharts ChartSchool:
  https://school.stockcharts.com/doku.php?id=chart_analysis:point_and_figure
  (verified: double-top breakout = X column exceeding the prior X column
  high; double-bottom breakdown = O column exceeding the prior O column
  low; 3-box reversal is the classic setting.)

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1% equity
risk per trade, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
longs and shorts allowed. WARMUP = 30 bars.

## Honest limitation (1h crypto)

A 1% box on 1h crypto is coarse relative to hourly noise: BTC needs a
~3% adverse move to flip a column, so columns persist for weeks and the
strategy trades rarely (30 BTC trades in ~7.5 months) — and, per
BACKTEST.md, nearly every trade ends at the stop, not at a reversal exit.
P&F was designed for daily/weekly charts over months; compressing it onto
1h bars keeps the textbook rules but loses much of its pattern context
(triple tops, catapults, price objectives are not used here). The
backtest verdict is a loser as shipped; do not mistake the classical
pedigree for an edge on this timeframe.
