# KAMA Cross

Perry Kaufman's Adaptive Moving Average cross — the fast
KAMA(ER 10, fast 2, slow 30) against the slow KAMA(ER 20,
fast 2, slow 30). The efficiency ratio makes the average
track price tightly in a clean trend (ER near 1, fast
smoothing) and go nearly flat in chop (ER near 0, slow
smoothing), so the cross of the two is a trend-change signal
that adapts to the market's own noise level.

- **Long:** fast KAMA crosses above slow KAMA
- **Short:** fast KAMA crosses below slow KAMA
- **Exit:** the opposite cross
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the cross itself as a safety net for gap-through
  moves)

Parameters: ER periods 10 (fast) / 20 (slow), fast smoothing
constant 2/(2+1) = 2/3, slow smoothing constant 2/(30+1) =
2/31, KAMA seeded at the first close. ATR(14) in the harness
for the stop/trail.

Source: Perry Kaufman, "Smarter Trading" (1995) —
https://docs.wickra.org/Indicators/Indicator-Kama

Usage:

```python
from strategies.kama_cross import indicators, signals, risk

df = indicators.add_indicators(df)  # er_fast=10, er_slow=20 defaults
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-25 Hyperliquid 1h
(BTC/ETH/HYPE, batch-46 pinned window) results and
CALIBRATION.md for the fast-ER 5/10/20 sensitivity check.
