# Two-Bar Key Reversal

Larry Williams' 2-bar key reversal — a single exhaustion bar plus
one confirmation bar.

- **Long:** bar i-1 is a down bar (close < open) AND makes a lower
  low than bar i-2, AND bar i closes above bar i-1's high
- **Short:** bar i-1 is an up bar AND makes a higher high than bar
  i-2, AND bar i closes below bar i-1's low
- **Exit:** the opposite reversal signal
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage

Parameters: confirmation mode `"high"` (shipped) / `"close"` /
`"none"` (see signals.py), ATR(14) for stop/trail.

Usage:

```python
from strategies.two_bar_reversal import indicators, signals, risk

df = indicators.add_indicators(df)
sig = signals.add_signals(df)   # confirm="high" default
```

See BACKTEST.md for the 2026-03-14 → 2026-11-24 Hyperliquid 1h
(BTC/ETH/HYPE) results — honest verdict: loser overall,
combined -$7,381.81 on 1,175 trades (BTC -$5,281.93, -52.81%;
HYPE the only positive coin, +$212.05, noise-level) — and
CALIBRATION.md for the high/close/none confirmation sweep (looser
confirmation is strictly worse).
