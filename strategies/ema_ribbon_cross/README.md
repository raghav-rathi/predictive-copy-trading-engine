# EMA Ribbon Expansion

A Guppy-style EMA ribbon (8/13/21/34/55) traded on compression
then expansion. When the five EMAs bunch together (ribbon width
at its 20-bar minimum) the market is coiled; when the ribbon then
expands with all five EMAs aligned, the move has room to run.
This is a single-ribbon construction — distinct from the shipped
`guppy_mma`, which averages two groups of six EMAs into two mean
lines.

- **Long:** ribbon fully aligned bullish (EMA8 > EMA13 > EMA21 >
  EMA34 > EMA55) AND compression was true within the last 3 bars
- **Short:** ribbon fully aligned bearish (EMA8 < EMA13 < EMA21 <
  EMA34 < EMA55) AND compression was true within the last 3 bars
- **Exit:** alignment breaks at the fast end — long exit when
  EMA8 < EMA13, short exit when EMA8 > EMA13
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage

Parameters: EMAs 8/13/21/34/55 of close; ribbon width =
(EMA8 − EMA55)/EMA55; compression = |width| at its 20-bar
minimum; compression window 20, recent window 3 bars. ATR(14)
in the harness for the stop/trail.

Usage:

```python
from strategies.ema_ribbon_cross import indicators, signals, risk

df = indicators.add_indicators(df)  # compression_window=20 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-25 Hyperliquid 1h
(BTC/ETH/HYPE, batch-46 pinned window) results — honest verdict:
loser combined (-$2,608 on 364 trades), with ETH the only
positive coin — and CALIBRATION.md for the compression-window
10/20/40 sensitivity check and the lookahead audit.
