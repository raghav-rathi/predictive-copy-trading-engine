# Pi Cycle Top

Philip Swift's Pi Cycle Top indicator (2019), run as a slow regime
system on 1h bars. Two simple moving averages of the close:

- **SMA(111)** vs **2.0 × SMA(350)** — the "top zone" is where
  SMA(111) ≥ 2.0 × SMA(350)
- **Long:** SMA(111) crosses back *below* 2.0 × SMA(350) (exiting
  the top zone)
- **Short:** SMA(111) crosses *above* 2.0 × SMA(350) (the top
  signal)
- **Exit:** the opposite cross — the regime itself is the trade
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, **no max hold**
  (a regime trade, not a scalp — see risk.py), 1% risk/trade,
  3x leverage

Parameters: SMA(111), SMA(350), multiplier 2.0, ATR(14) for
stop/trail.

Usage:

```python
from strategies.pi_cycle import indicators, signals, risk

df = indicators.add_indicators(df)   # mult=2.0 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-24 Hyperliquid 1h
(BTC/ETH/HYPE, batch-45 frozen window) results — honest verdict:
**zero trades on all three coins**; the ratio never got near 2.0
on 1h bars in this window (peak 1.13 BTC / 1.17 ETH / 1.22 HYPE),
so the system is untestable here, not a winner or a loser — and
CALIBRATION.md for the 1.9/2.0/2.1 multiplier sweep (also all
zeros).
