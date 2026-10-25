# EMA Crossover

The textbook moving-average trend signal, shipped bare: long when
EMA(9) crosses above EMA(21), short on the cross below, exit on the
opposite cross. No filters, no confirmation, no regime gate — the
backtest measures exactly what the classic signal is worth on 1h
crypto, fees included.

## Rules

- Long entry: EMA(9) crosses above EMA(21)
- Short entry: EMA(9) crosses below EMA(21)
- Exit: the opposite cross (longs exit on a cross down, shorts on a
  cross up)
- Risk: 2xATR stop, 2.5xATR chandelier trail, no fixed target,
  168-bar (7-day) max hold, 1% equity risk per trade, 3x leverage cap

## Why this parameterization

EMA(9)/EMA(21) is the short-term crossover pair most often quoted for
intraday trend-following. The 2xATR stop is deliberately roomy:
crossovers whipsaw, and a tight stop just pays fees faster. The
opposite cross is the only signal exit — the trade lives or dies by
the trend the cross identified.

Source: moving-average crossover (Murphy, Technical Analysis of the
Financial Markets).
