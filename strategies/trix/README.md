# TRIX Momentum Turn

Momentum-turn entries on Jack Hutson's TRIX — a triple-smoothed
exponential oscillator (early 1980s).

- **EMA1** = EMA(close, 14), **EMA2** = EMA(EMA1, 14),
  **EMA3** = EMA(EMA2, 14)
- **TRIX** = 100 × (EMA3 − EMA3.shift(1)) / EMA3.shift(1)
- **Signal** = EMA(TRIX, 9)
- **Long:** TRIX crosses above its signal while still below zero
  (momentum turns up from washed-out territory)
- **Short:** TRIX crosses below its signal while still above zero
- **Exit:** the opposite cross, regardless of territory (a cross the
  other way means the turn failed)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 200-bar max hold
  (slow oscillator — give legs room), 1% risk/trade, 3x leverage

Parameters: len=14, sig_n=9, ATR(14) for stop/trail. WARMUP=80
(triple-EMA spin-up).

Usage:

```python
from strategies.data import fetch_candles
from strategies.trix import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))  # len=14, sig=9 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the len=10/14/21 sensitivity check.

Source: TRIX (Jack Hutson) —
https://capital.com/en-eu/learn/technical-analysis/trix-indicator
