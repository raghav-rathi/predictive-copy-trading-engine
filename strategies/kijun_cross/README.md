# Kijun Cross

The Kijun-sen is Ichimoku's baseline: the midpoint of the last 26 bars' range. It moves only when the range's extremes change, so it is flat through chop and steps with real breaks. This system strips Ichimoku down to that one line — price crossing above it is long, below it short — to test whether the baseline alone carries any edge without the cloud's confirmation.

## Mechanism

- Kijun-sen(26) = (26-bar highest high + 26-bar lowest low) / 2.
- The line is a step function of the range extremes, not a smoothed average.
- No Tenkan, cloud, or Chikou filter is applied.

## Entry / exit

- **Long entry:** close crosses above Kijun-sen.
- **Short entry:** close crosses below Kijun-sen.
- **Exit:** the opposite cross. The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- Ichimoku Kijun-sen (Goichi Hosoda):
  https://school.stockcharts.com/doku.php?id=technical_indicators:ichimoku_cloud

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 40 bars
(26 bars for Kijun-sen + ATR/margin.).

## Honest limitation

A 26-bar range midpoint lags badly on 1h bars and, being flat for long stretches, generates crosses exactly when price snaps through a stale level — often the worst moment to chase. Without the cloud filter this is the noisiest possible Ichimoku reduction (see BACKTEST.md).

Paper only, no live execution.
