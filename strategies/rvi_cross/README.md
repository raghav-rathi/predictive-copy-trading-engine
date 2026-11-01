# RVI Cross

John Ehlers' Relative Vigor Index measures trend conviction from
where price closes inside its bar: closes near the top of the range
mean buyers are in control, closes near the bottom mean sellers are.
The RVI / signal-line cross is the trade signal.

## Mechanism

- Numerator: (1,2,2,1)-weighted close−open over four bars.
- Denominator: (1,2,2,1)-weighted high−low over four bars.
- RVI = SMA(10) of numerator / SMA(10) of denominator.
- Signal line: the same (1,2,2,1) weighting applied to RVI itself.

## Entry / exit

- **Long entry:** RVI crosses above its signal line.
- **Short entry:** RVI crosses below its signal line.
- **Exit:** the opposite cross. The risk layer adds a 2xATR stop, a
  2.5xATR trail, and a 120-bar max hold.

## Source

- Relative Vigor Index (John Ehlers):
  https://www.investopedia.com/terms/r/relative_vigor_index.asp

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 20 bars
(13 bars for the weighted SMA(10) + ATR/margin.).

## Honest limitation

RVI is a centered oscillator built from open/close placement, so
it whipsaws whenever bars close mid-range — which is most of the
time in chop. The signal cross has no trend filter, so sideways
markets generate repeated small losses (see BACKTEST.md).

Paper only, no live execution.
