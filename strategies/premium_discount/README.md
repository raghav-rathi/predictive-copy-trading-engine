# Premium/Discount

ICT premium/discount equilibrium: a rolling 48-bar dealing
range defines equilibrium (the midpoint), a premium zone
(top 25% of the range) and a discount zone (bottom 25%).
Price sweeping one extreme and then reclaiming the midpoint
is the setup — the sweep is treated as a failed breakdown
rather than the start of a real break.

- **Long:** close crosses above eq AND the low touched the
  discount zone in the last 12 bars
- **Short:** close crosses below eq AND the high touched the
  premium zone in the last 12 bars
- **Exit:** the opposite cross of equilibrium
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage

Parameters: range lookback 48 bars, touch window 12 bars,
premium/discount at 75%/25% of the range, ATR(14) for
stop/trail.

Usage:

```python
from strategies.premium_discount import indicators, signals, risk

df = indicators.add_indicators(df)  # lookback=48 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-24 Hyperliquid 1h
(BTC/ETH/HYPE, batch-45 frozen window) results — honest verdict:
loser overall (-$1,987.40 combined on 816 trades), winning only
on HYPE (+$1,552.77) — and CALIBRATION.md for the 24/48/96
lookback sensitivity check, re-run on the same window.
