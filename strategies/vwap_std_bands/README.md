# VWAP Std Bands

## Mechanism

The UTC-day session VWAP is the volume-weighted average
price since UTC midnight: cumulative typical price
((high + low + close) / 3) times volume, divided by
cumulative volume, resetting each UTC day (crypto trades
24/7, so the calendar day is the session). Bands are drawn
at VWAP +/- 1 sigma and +/- 2 sigma, where sigma is the
strategy's specified practical proxy: the 20-bar rolling
standard deviation of (close - VWAP). (The textbook sigma
would use typical price minus VWAP over the session so far;
close minus VWAP over a trailing 20 bars is the documented
proxy — it tracks the same dispersion with a fixed,
causal window. For the first bars of a UTC day the trailing
window may straddle midnight; the VWAP itself always resets
with the day.)

- **Long entry:** a close that touched or breached the -2
  sigma band on the previous bar closes back above it on
  this bar — a rejection of an extreme downside excursion.
- **Short entry:** mirror at the +2 sigma band.
- **Exit:** the close reaches the VWAP midline.
- **Risk layer:** 2xATR stop, 2.5xATR trailing stop, 120-bar
  max hold, 1% risk per trade, 3x leverage cap.

## Source

VWAP (StockCharts ChartSchool, technical indicators: VWAP)
https://school.stockcharts.com/doku.php?id=technical_indicators:vwap

Note on verification: a direct fetch of this page failed in
the build environment with a tool-side error (not a confirmed
404), so the link is retained as specified in the batch brief
rather than claimed as freshly verified; the VWAP formula
(typical price, cumulative price x volume / cumulative
volume, resetting with the session) is corroborated by
StockCharts ChartSchool search results returned during the
build.

## Honest caveats

- The backtest (see BACKTEST.md) is a clear loser: -$8,103
  combined over 695 trades, 48.9% win rate, profit factor
  ~0.6 per coin. A near-coin-flip win rate with losers
  larger than winners is the signature of fading moves that
  keep trending.
- On 1h bars a 2-sigma excursion is often the start of a
  trend leg, not an exhaustion — mean reversion to the
  session VWAP is a weak thesis at this timeframe.
- Paper/backtest only. Nothing here touches live execution.
