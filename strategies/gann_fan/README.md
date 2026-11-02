# Gann Fan

Gann's fan draws angle lines from swing anchors: the 1x1 line advances one price unit per bar. This version anchors the rising fan at the 30-bar swing low and the falling fan at the 30-bar swing high, with the 'one unit' set to one ATR(14) so the angle scales with the coin's own volatility instead of an arbitrary price step. Crossing the fan is the trend signal.

## Mechanism

- Rising fan: 30-bar swing low + ATR(14) x bars since that low.
- Falling fan: 30-bar swing high - ATR(14) x bars since that high.
- Anchors roll every bar; a new extreme re-anchors its fan.

## Entry / exit

- **Long entry:** close crosses above the rising fan.
- **Short entry:** close crosses below the falling fan.
- **Exit:** the opposite fan cross. The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- Gann fan angles (W.D. Gann):
  https://www.investopedia.com/terms/g/gannfan.asp

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 44 bars
(30 bars for the swing anchor + ATR/margin.).

## Honest limitation

The fan slope is a modelling choice, not a law of nature: ATR per bar makes the angle volatility-scaled, but a volatility spike steepens the fan mid-trend and strands price below it, while calm periods flatten it until it means nothing. Gann's angles were drawn by hand from major pivots; a rolling 30-bar anchor is a much noisier substitute (see BACKTEST.md).

Paper only, no live execution.
