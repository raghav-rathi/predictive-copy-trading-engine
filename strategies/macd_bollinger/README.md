# MACD Bollinger

## Mechanism

Bollinger Bands are normally drawn on price. Here they are
drawn on the MACD line itself (the Carter setup from John
Carter's *Mastering the Trade*): MACD = EMA(12) − EMA(26),
signal = EMA(9) of the MACD line, and the bands are
SMA(20) ± 2 standard deviations of the MACD line. When the
MACD line stretches outside its own bands the momentum move
is overextended relative to its own recent history; the cross
back inside the band is the release.

- **Long entry:** MACD crosses back up through its own lower
  band while still below zero.
- **Short entry:** MACD crosses back down through its own
  upper band while still above zero.
- **Exits:** MACD crosses its band midline or its signal line
  in the adverse direction, whichever comes first.
- **Risk layer:** 2xATR stop, 2.5xATR trailing stop, 168-bar
  max hold, 1% risk per trade, 3x leverage cap.

## Source

Bollinger Bands on MACD (John Carter, *Mastering the Trade*;
MACD construction per StockCharts ChartSchool)
https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/moving-average-convergence-divergence-macd

## Honest caveats

- The backtest (see BACKTEST.md) loses on all three coins
  (-$5,711 over 417 trades, worst leg BTC -$2,377, Sharpe
  -2.41). Band-edge releases on 1h crypto behave more like
  continuation pauses than turns in this window.
- The stop dominates exits (320 stop / 97 signal): most
  releases keep running against the trade past the 2xATR
  stop before any midline exit can fire.
- Paper/backtest only. Nothing here touches live execution.
