# RSI Bollinger Bands

Bollinger Bands applied to RSI itself: instead of fixed 30/70
levels, the overbought/oversold lines adapt to RSI's own recent
history. A cross back inside the bands from an extreme is the
mean-reversion entry.

## Mechanism

- RSI(14), Wilder smoothing.
- Bands: SMA(20) of RSI ± 2 standard deviations of RSI.
- RSI above its upper band = stretched high relative to its own
  history; below its lower band = stretched low.
- The middle band is the exit: RSI reverting to its own mean.

## Entry / exit

- **Long entry:** RSI crosses above its lower band.
- **Short entry:** RSI crosses below its upper band.
- **Exit:** RSI crosses its middle band. The risk layer adds a
  2xATR stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- Bollinger Bands on RSI (mean-reversion construction):
  https://www.luxalgo.com/blog/mean-reversion-strategies-for-algorithmic-trading/
  (The bands-on-RSI construction itself is this strategy's own
  application of the standard Bollinger + RSI mean-reversion
  toolkit, not the source's exact setup.)

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 50 bars
(34 bars for RSI(14) + bands(20) + margin.).

## Honest limitation

Bands on an oscillator double-smooth the signal: RSI already lags
price, and its bands lag RSI. In trends RSI rides a band for weeks
of 1h bars, so 'leaving the band' often marks a pause, not a
reversal (see BACKTEST.md).

Paper only, no live execution.
