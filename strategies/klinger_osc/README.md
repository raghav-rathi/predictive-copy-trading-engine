# Klinger Volume Oscillator

A volume-force momentum system on Stephen Klinger's oscillator: each
bar's *volume force* — volume times a normalized range term, signed by
the bar's trend direction — is accumulated through a cumulative-range
`cm` term that resets whenever the typical-price trend flips, then
smoothed into the oscillator `kvo = EMA(VF,34) − EMA(VF,55)` against a
13-EMA signal line.

- **Long:** `kvo` crosses above the signal line
- **Short:** `kvo` crosses below the signal line
- **Exit:** the opposite cross (pure cross-based)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 150-bar max hold,
  1% risk/trade, 3x leverage

Parameters: kvo_fast=34, kvo_slow=55, signal=13, ATR(14) for stop/trail.

Usage:

```python
from strategies.data import fetch_candles
from strategies.klinger_osc import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=240)
sig = signals.add_signals(indicators.add_indicators(df))  # signal=13 default
```

See BACKTEST.md for the 2026-03-14 → 2026-10-21 Hyperliquid 1h
(BTC/ETH/HYPE) results and CALIBRATION.md for the 9/13/21 signal-line
sensitivity check.
