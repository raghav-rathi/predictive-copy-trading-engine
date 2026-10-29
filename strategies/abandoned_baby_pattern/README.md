# Abandoned Baby Pattern

## Mechanism

The abandoned baby (Steve Nison) is a 3-bar reversal built
from two gaps around a doji — the market gaps away from the
prior trend, pauses on a doji that touches nothing, then gaps
back the other way. All gaps here are strict: no overlap is
allowed between adjacent candles, which is what separates an
abandoned baby from an ordinary doji star.

Bullish abandoned baby (bars i-2, i-1, i):
- Bar i-2: long black candle (bearish, body >= 40% of range).
- Bar i-1: doji (body <= 10% of range) gapping DOWN — doji
  high below bar i-2's low.
- Bar i: long white candle (bullish, body >= 40% of range)
  gapping UP — bar i low above the doji high, close above
  the midpoint of bar i-2, and volume at/above the prior
  20-bar average (participation confirmation).

Bearish abandoned baby mirrors every condition.

## Entry / exit rules

- Long entry: bullish abandoned baby bar (the third
  candle's close) while flat.
- Short entry: bearish abandoned baby bar while flat.
- Long exit: a bearish baby bar while long. Short exit
  mirrors.
- Risk layer: 1.5xATR stop, 2xATR trail, 2.5xATR target,
  120-bar (5-day) max hold, 1% risk per trade, 3x leverage
  cap.

## Source

Abandoned baby pattern (Steve Nison, Japanese Candlestick
Charting Techniques) — Investopedia
https://www.investopedia.com/terms/a/abandonedbaby.asp

## Honest caveats

- The backtest (see BACKTEST.md) produces ZERO trades on all
  three coins over the full ~7.5-month window. This is not a
  detector bug — the unit tests fire both variants on
  synthetic data — it is structural: crypto trades 24/7, so
  true gaps between 1h candles essentially never occur
  (0 gap-doji sequences on BTC and ETH, 1 on HYPE, which
  then failed the remaining filters). The pattern is an
  equities-market pattern that assumes an overnight close;
  on continuous crypto it has no frequency to trade.
- A "no-trade" result is not a win, a loss, or an edge — it
  is evidence the setup does not exist in this market at
  this timeframe. Relaxing the gap rule to manufacture trades
  would turn it into a different pattern (a doji star) and
  was not done.
- Paper/backtest only. Nothing here touches live execution.
