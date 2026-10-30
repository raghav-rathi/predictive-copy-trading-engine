# Multi-Timeframe Stack

4h trend filter + 1h EMA-cross entries — a genuinely different mechanism
from single-timeframe crosses, because the direction filter lives on a
different timeframe from the entry trigger.

## Mechanism

- **4h bars, built causally:** the 1h closes are grouped every 4
  consecutive bars; a 4h bar only exists once its 4th hour has closed. A
  1h bar therefore sees only 4h bars completed before it — the
  in-progress 4h bar is never used, so there is no lookahead.
- **4h trend:** EMA(20) on 4h closes above EMA(50) on 4h closes =
  uptrend; below = downtrend.
- **1h entry:** EMA(9) crosses above EMA(21) on 1h closes while the 4h
  trend is up → long; EMA(9) crosses below EMA(21) while the 4h trend
  is down → short.

## Entry / exit

- **Long entry:** 1h bullish EMA cross + 4h uptrend.
- **Short entry:** 1h bearish EMA cross + 4h downtrend.
- **Exit:** the opposite 1h EMA cross (regardless of the 4h trend at
  that moment). The risk layer adds a 2xATR stop, a 2.5xATR trail, and a
  120-bar max hold.

## Source

- Multiple timeframe analysis (higher timeframe sets the trend, lower
  timeframe times the entry; higher timeframe wins on conflict):
  https://collinseow.com/multi-timeframe-analysis/
  (verified; the 4h/1h pairing and EMA choices are this strategy's own
  construction, not the source's.)

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1% equity
risk per trade, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
longs and shorts allowed. WARMUP = 230 bars (50 completed 4h bars = 200
1h bars, plus the 1h EMA(21) lookback and margin).

## Honest limitation

Groups are formed by position in the sorted 1h series, not by wall-clock
hour, so an occasional missing hour would shift group boundaries; on
this window the bars are consecutive hours, so groups align with
00/04/08/12/16/20 UTC blocks. The 4h filter is also slow: a 4h trend flip
lags a 1h reversal by hours, so entries late in a 4h trend still face
the same whipsaw as a plain 1h cross — the filter cuts trade count
rather than eliminating false crosses (see BACKTEST.md).
