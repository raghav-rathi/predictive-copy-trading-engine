# Hull Suite

InSilico's Hull Suite trades the Hull Moving Average's own slope: the line is green and rising in an uptrend, red and falling in a downtrend, and the turn itself is the signal. HMA(16) is built to cut lag — double the fast WMA, subtract the slow WMA, smooth over 4 bars — so its turns arrive earlier than an EMA's, at the cost of overshooting violent reversals.

## Mechanism

- HMA(16) = WMA(2 x WMA(close, 8) - WMA(close, 16), 4).
- Bands: HMA +/- 1.5 x ATR(14), context only, not traded.
- Trend = sign of the HMA's bar-to-bar change.

## Entry / exit

- **Long entry:** HMA turns up.
- **Short entry:** HMA turns down.
- **Exit:** the opposite turn. The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- Hull Suite (InSilico) / Hull Moving Average (Alan Hull):
  https://arrowalgo.com/hull-moving-average-strategy/

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 32 bars
(16 bars for HMA + 4-bar smoothing + ATR/margin.).

## Honest limitation

The HMA's extrapolation overshoots: on a violent reversal it swings past the move before correcting, so turn signals fire, reverse, and fire again. In a range the line turns on every wiggle and the system bleeds fees — the Suite's own literature pairs it with a trend filter, which this standalone version deliberately omits to keep the test honest (see BACKTEST.md).

Paper only, no live execution.
