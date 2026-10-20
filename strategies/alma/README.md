# ALMA Dual Cross

Trend-following on the Arnaud Legoux Moving Average — a
Gaussian-weighted moving average (sigma=6) whose bell is pulled toward
the newest bars (offset=0.85), so it hugs price with less lag than a
symmetric smoothing while staying calmer than a short EMA.

- **Long:** ALMA(9) crosses above ALMA(21) **and** the close is a new
  20-bar high (fresh extreme = momentum actually left the box)
- **Short:** ALMA(9) crosses below ALMA(21) **and** the close is a new
  20-bar low
- **Exit:** the opposite cross (pure cross-based, no breakout filter)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 200-bar max hold,
  1% risk/trade, 3x leverage

Parameters: offset=0.85, sigma=6, fast=9, slow=21, breakout window 20
bars, ATR(14) for stop/trail.

Usage:

```python
from strategies.data import fetch_candles
from strategies.alma import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=240)
sig = signals.add_signals(indicators.add_indicators(df))  # offset=0.85 default
```

See BACKTEST.md for the 2026-03-14 → 2026-10-20 Hyperliquid 1h
(BTC/ETH/HYPE) results and CALIBRATION.md for the 0.75/0.85/0.95
offset sensitivity check.
