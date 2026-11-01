# Inverse Fisher RSI

John Ehlers' Inverse Fisher Transform applied to a 5-bar RSI: the
transform compresses the RSI into a bipolar (-1, +1) oscillator
that sits near +1 in uptrends and near −1 in downtrends, so
threshold crossings give sharp black-or-white signals.

## Mechanism

- RSI(5), Wilder smoothing.
- value1 = 0.1 × (RSI − 50), scaling the RSI into (−5, +5).
- value2 = 9-bar linearly weighted average of value1.
- IFish = (e^(2·value2) − 1) / (e^(2·value2) + 1) = tanh(value2).
- The ±0.5 thresholds mark the strong zones: above +0.5 is
  strongly bullish, below −0.5 strongly bearish.

## Entry / exit

- **Long entry:** IFish crosses above −0.5 (leaving the bearish
  pole).
- **Short entry:** IFish crosses below +0.5 (leaving the bullish
  pole).
- **Exit:** IFish crosses back out of the strong zone in the
  trade's direction. The risk layer adds a 2xATR stop, a 2.5xATR
  trail, and a 120-bar max hold.

## Source

- Inverse Fisher Transform (John Ehlers):
  https://c.mql5.com/forextsd/forum/59/the_inverse_fisher_transform.pdf

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 20 bars
(13 bars for RSI(5) + WMA(9) + ATR/margin.).

## Honest limitation

The bipolar compression is the weakness as well as the strength:
IFish saturates, so it cannot distinguish a strong trend from an
extreme one, and a 5-bar RSI flips poles on any two-bar reversal.
Threshold crossings in chop fire constantly (see BACKTEST.md).

Paper only, no live execution.
