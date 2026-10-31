# HalfTrend

Everget's open-source HalfTrend trailing-stop trend system: amplitude-2
price extremes plus SMA(high/low) confirmation drive a two-state trend
machine. The trend line trails price and never reverses against the
current trend; a flip of the trend state is the signal.

## Mechanism

- **Extremes (amplitude = 2):** highPrice = the high at the bar with the
  highest high in the last 2 bars; lowPrice = the low at the bar with
  the lowest low in the last 2 bars.
- **Confirmation MAs:** highma = SMA(high, 2), lowma = SMA(low, 2).
- **State machine (trend 0 = uptrend, 1 = downtrend, HalfTrend's own
  convention):** maxLowPrice starts at the prior low (or low),
  minHighPrice at the prior high (or high).
  - If nextTrend == 1: maxLowPrice = max(lowPrice, prev maxLowPrice);
    if highma < maxLowPrice AND close < prev low, trend becomes 1
    (down), nextTrend becomes 0, minHighPrice = highPrice.
  - If nextTrend == 0: minHighPrice = min(highPrice, prev minHighPrice);
    if lowma > minHighPrice AND close > prev high, trend becomes 0
    (up), nextTrend becomes 1, maxLowPrice = lowPrice.
- **Trend line:** in an uptrend the line is max(maxLowPrice, prev up)
  on continuation, and is initialised from the previous down line on a
  transition from down; in a downtrend it is min(minHighPrice, prev
  down) on continuation, initialised from the previous up line on a
  transition from up.
- **Channels (documented, not traded):** trend line +/- channelDeviation
  * (ATR(100) / 2), with channelDeviation = 2, so the channel width is
  exactly ATR(100).

## Entry / exit

- **Long entry:** trend flips 1 -> 0.
- **Short entry:** trend flips 0 -> 1.
- **Exit:** the opposite flip (a flip bar both exits the open side and
  enters the other side). The risk layer adds a 2xATR stop, a 2.5xATR
  trail, and a 120-bar max hold.

## Source

- Everget HalfTrend, open-source TradingView indicator
  (algorithm documentation, verified):
  https://deepwiki.com/everget/tradingview-pinescript-indicators/2.1.2-halftrend
- TradingView script page:
  https://in.tradingview.com/script/U1SJ8ubc-HalfTrend/
- The amplitude = 2 and channelDeviation = 2 values are the indicator's
  defaults; the flip-as-entry rule is this strategy's construction.

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1% equity
risk per trade, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
longs and shorts allowed. WARMUP = 110 bars (ATR(100) plus margin).

## Honest limitation

With amplitude = 2 the extremes and MAs react to nearly every bar, so
the state machine flips often in chop and the 2xATR stop manages most
trades (see BACKTEST.md: ~79% of exits are stops). The ATR channels
are context only and are not used for entries, exits, or filtering.
Paper only, no live execution.
