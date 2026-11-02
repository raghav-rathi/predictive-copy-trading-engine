# Keltner Breakout

Keltner's channel wraps price in an ATR envelope around EMA(20). Most Keltner systems fade the bands; this one does the opposite — a close outside a wide 2xATR channel is treated as a volatility breakout with momentum behind it, entered in the breakout direction and held until price gives the whole excursion back to the midline.

## Mechanism

- Midline = EMA(20) of close.
- Bands = midline +/- 2.0 x ATR(10).
- The 2.0 multiplier (vs the usual 1.5) keeps routine noise inside the channel.

## Entry / exit

- **Long entry:** close crosses above the upper band.
- **Short entry:** close crosses below the lower band.
- **Exit:** close returns to the midline. The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- Keltner channels (Chester Keltner):
  https://school.stockcharts.com/doku.php?id=technical_indicators:keltner_channels

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 30 bars
(20 bars for EMA(20) + ATR/margin.).

## Honest limitation

Breakout entries buy the extreme by definition: after a 2xATR excursion, mean reversion back inside the channel is the common outcome, and the midline exit then hands back the excursion plus fees. The system needs genuine momentum continuation to win, which 1h crypto breakouts often fail to deliver (see BACKTEST.md).

Paper only, no live execution.
