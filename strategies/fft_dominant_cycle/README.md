# FFT Dominant Cycle

Rolling FFT on detrended log-closes; trade the slope of the
reconstructed dominant cycle through an SMA(50) trend filter.

- **Window:** 128 bars, Hann window, linear detrend inside the window
- **Reconstruction:** top-3 dominant frequencies with period 8–64 bars
- **Trend filter:** SMA(close, 50)
- **Long:** reconstructed-cycle slope turns up and close > SMA(50)
- **Short:** slope turns down and close < SMA(50)
- **Exit:** slope flips sign, or price crosses SMA(50) against the position
- **Risk:** 1.5xATR stop, 2.5xATR target, 96-bar max hold, 1% risk/trade,
  3x leverage

Parameters: window=128, top_k=3, period 8–64, SMA(50). WARMUP=180
(128-bar FFT window + SMA(50) spin-up + margin).

Usage:

```python
from strategies.data import fetch_candles
from strategies.fft_dominant_cycle import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=365)
sig = signals.add_signals(indicators.add_indicators(df))  # top_k=3 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the top_k 1 – 3 – 5 sensitivity check.

Source: Fourier Transform Based Trading Strategy (PyQuantLab) —
https://pyquantlab.medium.com/a-fourier-transform-based-trading-strategy-in-backtrader-5e2d5a6d8392

## Honest caveats

- The FFT assumes stationary cycles; crypto cycles drift, so the
  reconstructed cycle is a lagging description of the last 128 bars,
  not a forecast. The backtest confirms it: combined -$9,840 on 986
  trades, red on all three coins, BTC -52.3% with MaxDD -56.1%.
- top_k=1 loses least in-sample (-$2,635) but is still red
  everywhere; the parameter moves how fast it loses, not whether it
  works.
- Single 8-month crypto window; no out-of-sample evidence.
