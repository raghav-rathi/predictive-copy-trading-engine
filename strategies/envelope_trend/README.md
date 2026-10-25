# MA Envelope Breakout

A fixed-percentage envelope: SMA(20) plus/minus 5%. Unlike ATR or
standard-deviation bands, the envelope does not adapt to volatility —
the market is "over-extended" only relative to its own recent average.
Traded here as a breakout (not a fade): long on a close above the
upper band, short on a close below the lower band, exit on a close
back through the midline.

## Rules

- Long entry: close crosses above SMA(20) x 1.05
- Short entry: close crosses below SMA(20) x 0.95
- Exit: close crosses back through the SMA(20) midline
- Risk: 2xATR stop, 2.5xATR chandelier trail, no fixed target,
  120-bar (5-day) max hold, 1% equity risk per trade, 3x leverage cap

## Why this parameterization

5% is wide for 1h bars — that is the point. The envelope is supposed
to fire rarely, only on genuine extensions. The backtest tests whether
rarity buys quality: fewer, bigger breakouts vs the constant churn of
tighter bands.

Source: moving-average envelopes (Murphy, Technical Analysis of the
Financial Markets).
