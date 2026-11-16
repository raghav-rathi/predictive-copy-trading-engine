# Wavelet Trend

DWT (db4, level 3) on closes; trade the slope of the
approximation-only reconstruction (the denoised trend).

- **Transform:** db4, level 3, pure-numpy filter bank, half-point
  symmetric extension (PyWavelets is not installed — the 8-tap
  Daubechies-4 coefficients are hardcoded in `indicators.py`)
- **Trend:** approximation-only reconstruction (all details zeroed)
- **Long:** approximation slope (5-bar window) turns positive and
  close is above the approximation
- **Short:** slope turns negative and close is below the approximation
- **Exit:** approximation slope flips, or close crosses the
  approximation the other way
- **Risk:** 1.5xATR stop, 2.5xATR target, 72-bar max hold, 1% risk/trade,
  3x leverage

Parameters: window=64, levels=3, slope window=5. WARMUP=64
(64-bar DWT window spin-up).

Usage:

```python
from strategies.data import fetch_candles
from strategies.wavelet_trend import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=365)
sig = signals.add_signals(indicators.add_indicators(df))  # levels=3 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the levels 2 – 3 – 4 sensitivity check.

Source: Wavelet Decomposition (LuxAlgo) —
https://www.luxalgo.com/library/concept/wavelet-decomposition/

## Honest caveats

- The level-3 approximation is genuinely smoother than raw closes
  (verified in tests: diff-std 2.60 → 0.22 on noisy trend data), but
  its 5-bar slope still flips constantly on 1h crypto — the backtest
  is the worst of this batch at -$18,401 on 1,792 trades, with BTC
  -72.1%.
- Boundary effects are documented in `indicators.py`: the symmetric
  extension keeps the edge bias small (~0.17 on a 0–10 ramp vs ~5.7
  for a periodic extension), but the approximation still lags the
  live trend.
- Single 8-month crypto window; no out-of-sample evidence.
