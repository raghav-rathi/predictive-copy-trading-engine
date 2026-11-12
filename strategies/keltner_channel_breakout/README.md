# Keltner Channel Breakout

Chester Keltner's channel breakout (*How to Make Money in
Commodities*, 1960), in the ATR form popularized by Linda Raschke in
the 1980s: the channel is an EMA(20) midline with bands two ATR(10)
above and below. A close outside the band is a volatility-expansion
breakout — the same family as the Wilder Volatility System, but the
band is anchored to a moving average rather than the previous bar's
range.

## Rules

- **Long entry:** close > EMA(20) + 2.0 * ATR(10) (upper band).
- **Short entry:** close < EMA(20) - 2.0 * ATR(10) (lower band).
- **Long exit:** close back inside the channel (close < upper band).
- **Short exit:** close back inside the channel (close > lower band).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail as the exit mechanism
  plus the channel-re-entry signal. Max hold 120 bars.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Chester Keltner, *How to Make Money in Commodities* (1960), ATR form popularized by Linda Raschke: https://www.investopedia.com/terms/k/keltnerchannel.asp

Paper only, no live execution.
