# Triple Top / Bottom

## Mechanism

A triple top is three rallies that stall at the same resistance
level; a triple bottom is the mirror at support. This engine
detects the pattern on 2-bar-lagged pivots (a pivot centered at
bar j is only usable from bar j+2, so no signal reads future
data):

- **Pivots:** a pivot high is the max high of its 5-bar window
  (j-2..j+2); a pivot low is the min low of its window.
- **Three tests:** the last three pivot highs sit within 1.5%
  of each other, consecutive pivots are separated by at least 5
  bars, and the first-to-last span is at most 60 bars.
- **Confirmation:** a close below the lowest intervening pivot
  low (triple top → short) or above the highest intervening
  pivot high (triple bottom → long). Unconfirmed triples never
  trade.

## Entry / exit rules

- Short entry: confirmed triple top bar.
- Long entry: confirmed triple bottom bar.
- Long exit: a triple top bar while long (opposite pattern).
  Short exit mirrors.
- Risk layer: 2xATR stop, 2.5xATR trailing stop, 168-bar max
  hold, 1% risk per trade, 3x leverage cap.

## Source

Classic triple top/bottom reversal — Edwards & Magee,
*Technical Analysis of Stock Trends*; StockCharts ChartSchool
https://chartschool.stockcharts.com/table-of-contents/chart-analysis/chart-patterns/triple-top-reversal

## Honest caveats

- The backtest (see BACKTEST.md) loses on all three coins:
  triple patterns are rare (130 trades in 7 months across three
  coins) and their neckline breaks do not follow through on 1h
  crypto in this window.
- Pivot detection on noisy 1h data is fragile: a 5-bar window
  pivot is a weak definition of "a test of resistance", and the
  1.5% tolerance band is a round-number choice, not a fitted
  one — but also not one with any evidence behind it on this
  asset class.
- The pattern fires once per triple, so a failed neckline break
  that retests and breaks again is missed by design.
- Paper/backtest only. Nothing here touches live execution.
