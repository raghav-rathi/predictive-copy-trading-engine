# Chaikin VWAP Combo

Marc Chaikin's Chaikin Money Flow (CMF) confirmed by the
UTC-day session VWAP. CMF weights each bar's volume by where
the close sits in the bar's range; the session VWAP is the
day's volume-weighted average price. A zero-cross of CMF with
price on the right side of the day's VWAP is the trade.

- **Long:** CMF(20) crosses above zero AND close > day VWAP
- **Short:** CMF(20) crosses below zero AND close < day VWAP
- **Exit:** CMF crosses back through zero OR the close crosses
  the day VWAP against the position
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage

Parameters: Money Flow Multiplier = ((C−L) − (H−C)) / (H−L)
(0 on a zero-range bar); Money Flow Volume = multiplier ×
volume; CMF(20) = sum(MFV, 20) / sum(V, 20); session VWAP
anchored to each UTC day. ATR(14) in the harness for the
stop/trail.

Usage:

```python
from strategies.chaikin_vwap_combo import indicators, signals, risk

df = indicators.add_indicators(df)  # cmf_window=20 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-25 Hyperliquid 1h
(BTC/ETH/HYPE, batch-46 pinned window) results — honest verdict:
the worst loser of my three by a wide margin (-$12,368 on
1,350 trades) — and CALIBRATION.md for the CMF-window 10/20/40
sensitivity check and the lookahead audit.
