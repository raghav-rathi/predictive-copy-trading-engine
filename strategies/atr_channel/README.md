# ATR Channel Breakout

A volatility-adjusted breakout channel: SMA(20) plus/minus 1.5x
ATR(14). In quiet markets the bands hug price; in wild markets they
widen. A close outside the channel is treated as a genuine breakout,
not noise — the channel width, not a fixed percentage, decides what
counts as "outside."

## Rules

- Long entry: close crosses above SMA(20) + 1.5xATR(14)
- Short entry: close crosses below SMA(20) - 1.5xATR(14)
- Exit: close crosses back through the SMA(20) midline (the breakout
  failed to hold)
- Risk: 2xATR stop, 3xATR chandelier trail (wider than the stop, so a
  real breakout has room to run), no fixed target, 120-bar (5-day)
  max hold, 1% equity risk per trade, 3x leverage cap

## Why this parameterization

The midline exit is the "breakout failed to hold" rule: a breakout
that falls back to the middle has lost its volatility justification.
This is the SMA-based ATR band construction (Wilder-style), distinct
from the Keltner variants already in the library, which use an EMA
midline.

Source: ATR bands / volatility channel (Wilder ATR; Murphy,
Technical Analysis of the Financial Markets).
