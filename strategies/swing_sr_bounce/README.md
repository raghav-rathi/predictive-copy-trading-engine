# Swing Support / Resistance Bounce

Support and resistance are where price has turned before: swing
highs and lows (5-bar zigzag, causal) from the last 250 bars are
clustered within 0.5% of each other, and a cluster with at least two
touches becomes a level. The trade is the bounce: long when a bar
dips to a support level and closes back above it with an up close,
short on the mirror at resistance. A close 0.5% beyond the level is
a failure, not a bounce.

## Rules

- Level: >=2 zigzag pivots within 0.5% of each other in the last
  250 bars.
- Long entry: bar low within 0.3% of support, close back above
  support, close above open.
- Short entry: bar high within 0.3% of resistance, close back below
  resistance, close below open.
- Exit: close 0.5% beyond the entry level (level failed), or the
  opposite bounce.
- Risk: 1.5xATR stop, 2xATR trail, no fixed target, 72-bar (3-day)
  max hold, 1% equity risk per trade, 3x leverage cap

## Why this parameterization

The bounce needs confirmation (close back above the level with an
up close) precisely because a touch without confirmation is just
price passing through. The backtest shows the confirmation isn't
enough (see BACKTEST.md): levels built from two touches on noisy 1h
data break more often than they hold.

Source: support / resistance bounce (Murphy, Technical Analysis of
the Financial Markets).
