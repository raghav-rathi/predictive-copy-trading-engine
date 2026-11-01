# Guppy MMA

Daryl Guppy's Multiple Moving Average (GMMA): twelve EMAs in two
ribbons — six fast (traders) and six slow (investors). The ribbon
cross is the trend-change signal; ribbon separation reads trend
strength.

## Mechanism

- Short group: EMA(3, 5, 8, 10, 12, 15) of close; its mean is the
  fast ribbon center.
- Long group: EMA(30, 35, 40, 45, 50, 60) of close; its mean is the
  slow ribbon center.
- The gap between the group means measures trend strength:
  expansion confirms a trend, compression warns of a turn.

## Entry / exit

- **Long entry:** short-group mean crosses above long-group mean.
- **Short entry:** short-group mean crosses below long-group mean.
- **Exit:** the opposite cross. The risk layer adds a 2xATR stop, a
  2.5xATR trail, and a 120-bar max hold.

## Source

- Guppy Multiple Moving Average (Daryl Guppy):
  https://capital.com/en-int/learn/technical-analysis/gmma-indicator

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 70 bars
(60 bars for EMA(60) + ATR/margin.).

## Honest limitation

A ribbon cross is still a moving-average cross: it lags real turns
and whipsaws in chop. The 60-bar slow ribbon is especially slow on
1h bars, so entries arrive days into a move and exits lag the
reversal (see BACKTEST.md).

Paper only, no live execution.
