# Volume Price Trend

Volume Price Trend: the running total of each bar's percentage
price change multiplied by its volume. Where OBV treats every up
bar equally, PVT weights by conviction — big moves on big volume
move the line most. Crosses of its 20-bar average mark momentum
shifts in volume-backed flow.

## Mechanism

- Each bar contributes volume × (close − prev close) / prev close.
- PVT is the cumulative sum; its level is arbitrary, only
  direction and slope matter.
- Signal line: SMA(20) of PVT. Crosses are momentum-shift markers,
  read the same way as MACD signal crosses.

## Entry / exit

- **Long entry:** PVT crosses above its 20-bar average.
- **Short entry:** PVT crosses below its 20-bar average.
- **Exit:** the opposite cross. The risk layer adds a 2xATR stop, a
  2.5xATR trail, and a 120-bar max hold.

## Source

- Price Volume Trend (PVT):
  https://docs.prorealalgos.com/pvt.html

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 40 bars
(20 bars for the PVT average + ATR/margin.).

## Honest limitation

PVT is a confirmation tool, not a timing tool: it inherits price's
own trend, so its average-cross mostly restates what price already
did, with volume noise on top. On 1h bars the cross count is high
and the edge over a plain price cross is unproven (see BACKTEST.md).

Paper only, no live execution.
