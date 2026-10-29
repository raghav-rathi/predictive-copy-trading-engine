# CCI Zero Cross

## Mechanism

The Commodity Channel Index (Donald Lambert) measures how far
the typical price sits from its 20-bar average, scaled by mean
deviation. Zero is the boundary between its bearish and
bullish halves: a cross above zero is the oscillator flipping
to its bullish regime, a cross below zero the flip to bearish.
This engine trades only those regime flips that agree with the
price trend:

- **Long entry:** CCI(20) crosses up through zero while price
  is above SMA(50).
- **Short entry:** CCI(20) crosses down through zero while
  price is below SMA(50).
- **Crosses against the trend are ignored** — a zero cross
  into the teeth of the SMA(50) trend is not a signal here.
- **Exits:** the opposite zero cross (a long that sees CCI
  cross back below zero has lost its regime).
- **Risk layer:** 2xATR stop, 3xATR trailing stop, 240-bar
  max hold, 1% risk per trade, 3x leverage cap.

This is deliberately not cci_divergence (pivot disagreement)
and not cci_extreme (the +/-100 return): the zero line plus
the trend filter are the entire signal.

## Source

CCI by Donald Lambert; zero-line interpretation per
StockCharts ChartSchool
https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/commodity-channel-index-cci

## Honest caveats

- The backtest (see BACKTEST.md) loses heavily (-$9,926 over
  920 trades, 24.9% win rate, BTC -43.8% max drawdown). The
  SMA(50) filter does not rescue the zero cross on 1h bars:
  CCI crosses zero as noise far more often than as regime
  change, and the trade count (920) is itself the tell.
- Paper/backtest only. Nothing here touches live execution.
