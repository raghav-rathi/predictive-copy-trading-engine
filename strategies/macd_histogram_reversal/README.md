# MACD Histogram Reversal

## Mechanism

The MACD histogram (MACD line minus its signal line, Alexander
Elder's construction in *Trading for a Living*) is the second
derivative of price momentum: its slope turns before the MACD
line itself turns. Elder's rule trades the slope flip — the
first uptick after a decline, or the first downtick after a
rise — with the histogram's own sign as the filter:

- **Long entry:** histogram trough flip (hist[i] > hist[i-1]
  after hist[i-1] <= hist[i-2]) while the histogram is still
  below zero.
- **Short entry:** histogram peak flip (mirror) while the
  histogram is still above zero.
- **Exits:** the opposite flip, or a zero cross in the
  adverse direction (the turn gave everything back).
- **Risk layer:** 2xATR stop, 2xATR trailing stop, 72-bar max
  hold, 1% risk per trade, 3x leverage cap.

A flip both exits one side and may enter the other on the
same bar — the harness exits first, then enters, which is the
intended reversal behaviour.

## Source

MACD Histogram (Alexander Elder, *Trading for a Living*;
MACD construction per StockCharts ChartSchool)
https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/moving-average-convergence-divergence-macd

## Honest caveats

- The backtest (see BACKTEST.md) is the worst in this batch:
  -$18,600 over 1,844 trades, Sharpe -3.79 to -6.34, max
  drawdowns -56% to -68%. The histogram's local slope flips
  on a large fraction of all 1h bars, so the strategy trades
  noise at maximum frequency, and two-thirds of trades end at
  the stop (1,193 stop / 651 signal).
- The sign filter helps (it halves the raw flip count) but
  does not fix the core problem: a second-derivative series
  wiggles constantly, and most wiggles are not turns.
- Paper/backtest only. Nothing here touches live execution.
