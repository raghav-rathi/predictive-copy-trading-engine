# Ehlers Instantaneous Trendline

John F. Ehlers' Instantaneous Trendline (*Cybernetic Analysis for
Stocks and Futures*, 2004): a near-zero-lag trend extractor built on
the idea that price is trend plus cycle. The trendline is a compact
recursive filter — a weighted blend of the last three closes and its
own last two outputs — governed by a single alpha coefficient
(Ehlers' default 0.07). Because it tracks the trend component almost
instantaneously, a close crossing the trendline marks a trend change
far earlier than a moving-average cross.

## Rules

- **Long entry:** close crosses above the Instantaneous Trendline.
- **Short entry:** close crosses below the Instantaneous Trendline.
- **Long exit:** close crosses below the trendline.
- **Short exit:** close crosses above the trendline.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail as the exit mechanism
  plus the opposite cross. Max hold 120 bars.

The trendline is seeded with the SMA of the closes available so far
(IT_0 = c_0, IT_1 = mean(c_0, c_1)); warmup is 60 bars, far longer
than the filter's settling time, so the seed has no effect on traded
bars. No trigger line (the 2-bar projected companion line) is used —
the spec fixes the plain close/trendline cross.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- John F. Ehlers, *Cybernetic Analysis for Stocks and Futures* (2004),
  Instantaneous Trendline, alpha 0.07:
  https://www.fmz.com/lang/en/strategy/436000

Paper only, no live execution.
