# Elder Force Index

Alexander Elder's Force Index pullback timing: buy the dip while the
bulls are in charge, sell the rally while the bears are.

- **Force Index:** `fi = (c − c.shift(1)) * v` — price change weighted
  by volume, the force behind a move.
- **Entry timer:** `fi2 = EMA(fi, 2)`; **trend gauge:**
  `fi13 = EMA(fi, 13)`.
- **Long:** fi13 > 0 (bulls in charge) **and** fi2 crosses below zero
  (the pullback). **Short:** fi13 < 0 and fi2 crosses above zero.
- **Exit:** fi13 itself crosses zero — the balance of power flipped,
  so the trend premise is gone.
- **Risk:** 2xATR stop (pullbacks need room), 3xATR chandelier trail,
  100-bar max hold, 1% risk/trade, 3x leverage.

Parameters: fast=2, trend=13, ATR(14). WARMUP=60.

Usage:

```python
from strategies.data import fetch_candles
from strategies.elder_force_index import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=240)
sig = signals.add_signals(indicators.add_indicators(df))  # trend_len=13 default
```

See BACKTEST.md for the 2026-03-14 → 2026-10-21 Hyperliquid 1h
(BTC/ETH/HYPE) results (loser: -$8,224 combined on 1,051 trades —
the fi2 zero-cross trigger churns into chop) and CALIBRATION.md for
the 9/13/21 trend-EMA sensitivity check.
