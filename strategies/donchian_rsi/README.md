# Donchian + RSI

Richard Donchian's 20-bar channel breakout (the core of the Turtle
system), with RSI(14) as the momentum confirmation. A close above the
highest high of the prior 20 bars is a breakout — but only if RSI is
already above 55, so the move has momentum behind it instead of being
a lone wick. The mirror image on the downside, with RSI below 45.
Exits are the opposite Donchian breakout: the trade is closed as soon
as price breaks the other side of the channel.

## Rules

- **Long entry:** close > prior 20-bar high AND RSI(14) > 55.
- **Short entry:** close < prior 20-bar low AND RSI(14) < 45.
- **Long exit:** close < prior 20-bar low (opposite Donchian breakout).
- **Short exit:** close > prior 20-bar high.
- The channel is the prior 20 bars' high/low, excluding the current
  bar — the standard Donchian definition.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Donchian Channel and RSI Strategy (IQ Option Wiki): https://iqoptionwiki.com/donchian-channel-and-rsi-strategy/

Paper only, no live execution.
