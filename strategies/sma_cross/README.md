# SMA Crossover

The slower, smoother sibling of ema_cross: long when SMA(20) crosses
above SMA(50), short on the cross below, exit on the opposite cross.
Same bare-crossover logic, slower averages — fewer signals, later
confirmation, less whipsaw in principle. The backtest tests whether
"slower" actually means "better" or just "later."

## Rules

- Long entry: SMA(20) crosses above SMA(50)
- Short entry: SMA(20) crosses below SMA(50)
- Exit: the opposite cross
- Risk: 2xATR stop, 2.5xATR chandelier trail, no fixed target,
  168-bar (7-day) max hold, 1% equity risk per trade, 3x leverage cap

## Why this parameterization

SMA(20)/SMA(50) is the medium-term crossover pair, slower than the
EMA(9)/EMA(21) pair by construction (SMAs weight all bars equally,
so they react later). The comparison with ema_cross is the point:
same risk, same exits, different speed.

Source: moving-average crossover (Murphy, Technical Analysis of the
Financial Markets).
