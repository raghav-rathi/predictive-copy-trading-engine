# CCI Divergence

## Mechanism

The Commodity Channel Index (Donald Lambert) measures how far
the typical price sits from its 20-bar average, scaled by mean
deviation. When price and the oscillator disagree at consecutive
pivot extremes, the move is losing momentum — the classic
divergence setup. This engine uses 2-bar-lagged price pivots (a
pivot centered at j is only usable from bar j+2) and attaches
each pivot's CCI value from the pivot bar itself:

- **CCI(20):** (typical price − SMA20) / (0.015 × mean deviation
  over 20 bars), mean deviation taken around the current bar's
  SMA (standard Lambert construction).
- **Bullish:** price makes a lower pivot low while CCI makes a
  higher pivot low, the two pivots within 40 bars, confirmed by
  a close above the prior 3-bar high within 20 bars of the
  second pivot.
- **Bearish:** mirror — higher price high, lower CCI high,
  close below the prior 3-bar low.

## Entry / exit rules

- Long entry: confirmed bullish divergence bar while flat.
- Short entry: confirmed bearish divergence bar while flat.
- Long exit: a bearish divergence bar while long. Short exit
  mirrors.
- Risk layer: 2xATR stop, 2.5xATR trailing stop, 168-bar max
  hold, 1% risk per trade, 3x leverage cap.

## Source

CCI by Donald Lambert; classic oscillator divergence —
StockCharts ChartSchool
https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/commodity-channel-index-cci

## Honest caveats

- The backtest (see BACKTEST.md) loses overall (-$962 over 156
  trades) despite two green legs: BTC's -$1,908 (PF 0.39,
  Sharpe -3.09) drags the whole book under. Divergence on BTC
  1h in this window is not a turn signal, it is a
  trend-continuation trap.
- The 3-bar-high confirmation is a weak trigger: it fires on
  ordinary counter-trend noise, and the 20-bar confirmation
  window lets stale divergences trade.
- Note the implementation detail: mean deviation is computed
  around the current bar's SMA (Lambert's definition), not as a
  rolling mean of per-bar deviations — the latter delays CCI
  by a full 20 bars and silently kills early divergences.
- Paper/backtest only. Nothing here touches live execution.
