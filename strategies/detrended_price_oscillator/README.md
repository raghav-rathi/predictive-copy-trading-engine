# DPO Zero-Line Cross

Detrended Price Oscillator cycle turns, filtered to trade only with
the primary trend (IncredibleCharts convention).

- **DPO(n)** = close − SMA(close, n) shifted back by `n//2 + 1` bars
  (the Ehlers/Investopedia displacement convention; n=20 → shift 11).
  Subtracting the displaced mean detrends price, so the oscillator
  shows where price sits inside its own dominant cycle: positive
  means price is above where the cycle says it should be.
- **Trend filter** = SMA(close, 50)
- **Long:** DPO crosses above zero while close > SMA(50)
  (cycle turns up inside an established uptrend)
- **Short:** DPO crosses below zero while close < SMA(50)
- **Exit:** the opposite zero-cross, regardless of the trend filter
  (once in, a cross the other way means the cycle itself turned)
- **Risk:** 2xATR hard stop, 2.5xATR chandelier trail, 150-bar max
  hold (~6 days — let a mid-frequency cycle play out), no fixed
  target, 1% risk/trade, 3x leverage

Parameters: n=20, ma=50, ATR(14) for stop/trail. WARMUP=80 (SMA(50)
spin-up is the binding constraint).

Usage:

```python
from strategies.data import fetch_candles
from strategies.detrended_price_oscillator import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))  # n=20, ma=50 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the n=10/20/30 sensitivity check.

Sources:
- DPO (Ehlers/Investopedia convention) —
  https://capital.com/en-eu/learn/technical-analysis/detrended-price-oscillator
- DPO trading rules (trend filter) —
  https://www.incrediblecharts.com/indicators/detrended_price_oscillator.php
