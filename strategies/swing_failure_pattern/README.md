# Swing Failure Pattern

Larry Williams' swing-failure / false-breakout pattern: a swing high
is the highest high of the prior 20 bars, a swing low the lowest low.
When price breaks a swing level but cannot hold it — closing back
inside within a few bars — the breakout traders are trapped and the
reversal is the trade. The classic form is a single candle that pokes
above the swing high (or below the swing low) and closes back inside.

## Rules

- **Short entry:** price makes a new 20-bar high (high > prior
  20-bar high) and then closes back below that swing high within the
  next 3 bars.
- **Long entry:** price makes a new 20-bar low (low < prior 20-bar
  low) and then closes back above that swing low within the next
  3 bars.
- **Long exit:** a bearish failure signal (the short-entry condition).
- **Short exit:** a bullish failure signal (the long-entry condition).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail as the exit mechanism
  plus the opposite failure. Max hold 120 bars.
- 20-bar swing window and 3-bar confirmation window are the standard
  values; nothing was tuned to this window.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Larry Williams — Swing Failure Pattern / false breakout: https://www.osl.com/hk-en/academy/article/what-is-the-swing-failure-pattern-and-how-to-use-it-in-trading

Paper only, no live execution.
