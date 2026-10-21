# Pretty Good Oscillator

Mark Johnson's breakout oscillator: `PGO = (close − SMA(14)) / SMA(ATR(14),14)`,
the close's distance from its 14-bar mean expressed in average true
ranges (dimensionless). Johnson framed it for breakout systems: a
|PGO| > 3 thrust is a genuine displacement, not noise. The denominator
is itself a 14-bar SMA of the ATR so one gap bar cannot collapse the
ratio.

- **Long:** PGO crosses above +3.0 (close thrusts more than 3 ATR above its SMA)
- **Short:** PGO crosses below −3.0
- **Exit:** PGO crosses back through 0 (the close returned to its 14-bar
  mean) — no trailing, no fixed target: the mean-reversion exit *is*
  the trade management
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 100-bar max hold,
  1% risk/trade, 3x leverage

Parameters: pgo_n=14, trigger=3.0, ATR(14) for stop/trail.

Usage:

```python
from strategies.data import fetch_candles
from strategies.pretty_good_osc import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=240)
sig = signals.add_signals(indicators.add_indicators(df))  # trigger=3.0 default
```

See BACKTEST.md for the 2026-03-14 → 2026-10-21 Hyperliquid 1h
(BTC/ETH/HYPE) results and CALIBRATION.md for the 2.0/3.0/4.0 trigger
sensitivity check.
