# Price Channel Breakout

Richard Donchian's price channel (1960s), the trend-following system
that later powered the Turtle Traders: the channel plots the highest
high and lowest low of the last N bars. A close beyond the channel is
a breakout — the market has made a new N-bar extreme — and the
midline (the average of the two bands) is the dynamic support /
resistance where the trade is given up.

## Rules

- **Long entry:** close breaks above the highest high of the prior
  30 bars.
- **Short entry:** close breaks below the lowest low of the prior
  30 bars.
- **Long exit:** close crosses back below the channel midline
  ((channel high + channel low) / 2).
- **Short exit:** close crosses back above the channel midline.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail as the exit mechanism
  plus the midline cross. Max hold 120 bars.

The channel uses the prior 30 bars only (the current bar excluded),
so a breakout close genuinely exceeds every high in the window.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Richard Donchian, Donchian Channel Breakout (Turtle Trading system):
  https://www.fintechvps.com/blog/donchian-channel-breakout

Paper only, no live execution.
