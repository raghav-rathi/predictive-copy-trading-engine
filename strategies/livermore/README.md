# Livermore

Jesse Livermore's trend system from "How to Trade in Stocks"
(1940): an uptrend is higher highs and higher lows, a
downtrend lower highs and lower lows — and the trade is the
breakout only when the structure behind it agrees.

- **Long:** close breaks above the prior 20-bar high AND the
  swing lows are rising (the 10-bar low ending 10 bars ago is
  higher than the 10-bar low ending 20 bars ago)
- **Short:** close breaks below the prior 20-bar low AND the
  swing highs are falling (lower highs)
- **Exit:** long exits on a close below the prior 10-bar low;
  short exits on a close above the prior 10-bar high
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage

Parameters: breakout lookback 20 bars, swing window 10 bars,
ATR(14) for stop/trail.

Usage:

```python
from strategies.livermore import indicators, signals, risk

df = indicators.add_indicators(df)  # breakout_lookback=20 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-24 Hyperliquid 1h
(BTC/ETH/HYPE, batch-45 window) results — honest verdict: the
least-bad loser of this batch (-$763.60 combined), winning only
on ETH — and CALIBRATION.md for the 10/20/30 breakout-lookback
check.
