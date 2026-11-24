# Three-Bar Reversal

Joe Ross' 3-bar reversal ("Trading by the Book") — a down bar,
then a hook bar that makes a new low but closes back up, then a
confirmation bar.

- **Long:** bar i-2 is a down bar; bar i-1 makes a lower low than
  bar i-2 AND closes above bar i-2's close; bar i closes above
  bar i-1's high
- **Short:** bar i-2 is an up bar; bar i-1 makes a higher high
  than bar i-2 AND closes below bar i-2's close; bar i closes
  below bar i-1's low
- **Exit:** the opposite reversal signal
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage

Parameters: confirmation mode `"high"` (shipped) / `"close"` /
`"none"` (see signals.py), ATR(14) for stop/trail.

Usage:

```python
from strategies.three_bar_reversal import indicators, signals, risk

df = indicators.add_indicators(df)
sig = signals.add_signals(df)   # confirm="high" default
```

See BACKTEST.md for the 2026-03-14 → 2026-11-24 Hyperliquid 1h
(BTC/ETH/HYPE) results — honest verdict: loser on all three coins,
combined -$7,688.32 on 982 trades (BTC -$5,737.97, -57.49%) — and
CALIBRATION.md for the high/close/none confirmation sweep (looser
confirmation is strictly worse).
