# EMA Triple Cross

## Mechanism

Three exponential moving averages — fast EMA(3), mid EMA(8),
slow EMA(21) — define the trend regime by their stacking
order. A market is bull-stacked when fast > mid > slow and
bear-stacked when fast < mid < slow. The system only trades
in the direction of the stack: no counter-trend entries, no
oscillator filter. This is the classic triple-moving-average
trend system, run here on 1h candles.

## Entry / exit rules

- Long entry: bull-stacked while flat.
- Short entry: bear-stacked while flat.
- Long exit: the stack stops being bull (any unstacking, even
  a one-bar EMA wobble) while long. Short exit mirrors.
- Risk layer: 2xATR stop, 3xATR chandelier trail, 336-bar
  (14-day) max hold, 1% risk per trade, 3x leverage cap.

## Source

Triple moving average system (classic trend system) —
StockCharts ChartSchool
https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/moving-averages

## Honest caveats

- The backtest (see BACKTEST.md) is a heavy loser: -$11,917
  across 1,451 trades, negative on all three coins, worst on
  BTC (-$6,080, Sharpe -4.98, max drawdown -62.4%). The
  unstack exit churns: 971 of 1,451 trades exit on signal
  (unstacking), so the system pays taker fees on every EMA
  wobble and rarely stays in a real trend long enough for
  the 3xATR trail to matter.
- Win rates of 23.6–31.2% with profit factors of 0.59–0.91
  say the stack is a lagging regime label, not a timing
  signal, on 1h crypto in this window.
- Paper/backtest only. Nothing here touches live execution.
