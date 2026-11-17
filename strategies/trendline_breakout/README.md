# Trendline Breakout

Demark-style trendline breaks: draw the trendline through the
last two swing pivots and trade the close breaking through it.

## Rules

- **Swing pivots (10-bar):** a swing high is a high strictly
  greater than the 5 bars on each side; a swing low is a low
  strictly less than the 5 bars on each side. A pivot formed at
  bar i is only confirmed at bar i+5, and the shipped code uses
  only confirmed pivots — a line through two pivots is only
  valid once the second pivot is confirmed.
- **Downtrend line:** straight line through the last two
  confirmed swing highs, extrapolated to the current bar.
- **Uptrend line:** straight line through the last two confirmed
  swing lows, extrapolated to the current bar.
- **Long entry:** close crosses above the downtrend line.
- **Short entry:** close crosses below the uptrend line.
- **Long exit:** close crosses below the uptrend line.
- **Short exit:** close crosses above the downtrend line.
- "Breaks" means a cross (previous close on the old side of the
  line, current close on the new side), not merely sitting beyond
  a line. A cross cannot fire on the bar a line first appears.
- The harness risk layer's 2xATR stop / 2.5xATR trail also
  applies. Max hold 120 bars.
- Warmup 120 bars.

All computation is causal, so signals on bar i use only data
through bar i's close.

## Source

- Thomas DeMark, TD trendlines (*The New Science of Technical
  Analysis*); trendline construction in general:
  https://www.investopedia.com/terms/t/trendline.asp

Paper only, no live execution.
