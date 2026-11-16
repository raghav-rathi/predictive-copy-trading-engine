# Volatility Quality Index

Stridsman VQI — trade the direction of "good" (directional)
volatility.

- **Efficiency:** e_t = (close_t − close_{t−1}) / true_range_t
- **Sum:** S_t = sum of e over the trailing 10 bars
- **VQI:** VQI_t = WMA(S, 14) (linear weights, newest heaviest)
- **Long:** VQI_t > VQI_{t−10} and |10-bar change| >= 0.5x its
  50-bar median (the no-trade gate)
- **Short:** VQI_t < VQI_{t−10} and the gate clears
- **Exit:** 10-bar VQI change flips sign, or the 20-bar EMA of
  close crosses against the position
- **Risk:** 1.5xATR stop, 2R target (2.0xATR), 48-bar max hold,
  1% risk/trade, 3x leverage

FROZEN CONVENTION: several published VQI variants exist (different
efficiency denominators, sum lengths, and smoothing); the one above
is exactly what is implemented here — see the module docstring in
`indicators.py` and CALIBRATION.md.

Parameters: eff_n=10, WMA=14, chg_n=10, gate median=50, gate
mult=0.5, EMA=20. WARMUP=60.

Usage:

```python
from strategies.data import fetch_candles
from strategies.volatility_quality_index import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=365)
sig = signals.add_signals(indicators.add_indicators(df))  # gate_mult=0.5 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the gate 0.0 – 0.5 – 1.0 sensitivity check.

Source: Alpha Volatility Quality (Stridsman VQI, Coder Wolves) —
https://in.tradingview.com/script/asS85p1B-Alpha-Trading-Alpha-Volatility-Quality-Coder-Wolves/

## Honest caveats

- The 10-bar VQI change flips sign almost every bar at 1h
  resolution, so the strategy is effectively always in a trade:
  3,742 trades in 8 months, $26,297 in fees, combined -$20,285,
  BTC -88.6%. The gate barely filters (|change| clears half its
  median ~75% of the time).
- A stricter gate (1.0x) loses least in-sample (-$15,571) but is
  still red everywhere; the gate moves how often it bleeds, not
  whether the sign predicts anything.
- Single 8-month crypto window; no out-of-sample evidence.
