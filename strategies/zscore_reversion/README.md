# Z-Score Reversion

Bollinger Bands restated as a z-score: how many standard deviations
price sits from its 20-bar mean. The documented mean-reversion
setup enters at |z| = 2 and exits when price reverts to the mean.

## Mechanism

- z = (close − SMA(20)) / std(20). z = ±2 is exactly the Bollinger
  band edge; z = 0 is the middle band.
- A cross below −2 means price stretched two deviations down;
  a cross above +2 means two deviations up.
- The exit is the reversion itself: z crossing back through zero.

## Entry / exit

- **Long entry:** z-score crosses below −2.
- **Short entry:** z-score crosses above +2.
- **Exit:** z-score crosses back through 0. The risk layer adds a
  2xATR stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- Bollinger z-score mean reversion:
  https://financefeeds.com/crypto-mean-reversion-strategy/

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 30 bars
(20 bars for SMA/std(20) + ATR/margin.).

## Honest limitation

Mean reversion assumes the mean is stable; in a trending market
the mean chases price and z stays pinned at extremes, so entries
fade a trend that keeps running. The 2xATR stop is wide relative
to a reversion target, so losers cost more than winners pay
(see BACKTEST.md).

Paper only, no live execution.
