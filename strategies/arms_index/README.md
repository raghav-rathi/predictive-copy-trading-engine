# ARMS Index (TRIN)

Panic-washout trading on the ARMS Index / TRIN, computed as a
single-asset candle/volume proxy.

- **TRIN:** (up-bars / down-bars) / (up-volume / down-volume) over
  a rolling 10-bar window; every component floored at 1
- **Long:** TRIN crosses below 0.7 after being above 1.0 in the
  prior 10 bars (panic washout)
- **Short:** TRIN crosses above 1.5 after being below 1.0 in the
  prior 10 bars
- **Exit:** TRIN reverts into the 0.9–1.1 band
- **Skip:** no trade if either 10-bar volume sum is 0
- **Risk:** 1.5xATR stop, 2xATR target, 24-bar max hold,
  1% risk/trade, 3x leverage

Parameters: window=10, long level 0.7, short level 1.5, band
0.9–1.1. WARMUP=20 (window + excursion lookback + margin).

Usage:

```python
from strategies.data import fetch_candles
from strategies.arms_index import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=365)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the 5 – 10 – 20 window sensitivity check.

Source: ARMS Index / TRIN (Richard Arms) —
https://investing.university/articles/arms-index-trin/

## Honest caveats

- **Single-asset proxy, not exchange-wide TRIN.** The real TRIN
  divides advancing by declining *issues* across an exchange. Here
  one coin's up/down candle counts and volumes stand in for the
  whole market — and the backtest says the proxy does not work:
  combined −$11,241 on 1,299 trades, every coin down 33%+, ETH
  max drawdown −52.5%.
- A 10-bar TRIN below 0.7 on one coin is usually a strong down-leg
  gathering pace, not a market panic flushing out — buying it
  catches a falling knife.
- The strategy trades ~5 times a day and pays $11,029 in fees to
  lose $11,241; transaction costs dominate the result.
- Single 8-month crypto window; no out-of-sample evidence.
