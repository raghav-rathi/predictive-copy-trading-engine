# Chaikin Volatility Expansion

Range-expansion entries on Marc Chaikin's Chaikin Volatility
oscillator, with an SMA50 trend filter.

- **Range EMA** = EMA(high − low, 10)
- **CV** = 100 × (Range EMA − Range EMA.shift(10)) / Range EMA.shift(10)
  — the rate of change of the average trading range
- **CV > 0:** average range is *expanding* (volatility rising);
  **CV < 0:** range contracting
- **Long:** CV crosses above +5.0 *and* close > SMA50 (volatility
  expansion starting in an uptrend)
- **Short:** CV crosses above +5.0 *and* close < SMA50
- **Exit:** CV crosses back below +5.0 *or* below 0 (the expansion
  rolls over — climactic participation is done)
- **Risk:** 2xATR hard stop, 1.5xATR chandelier trail, 100-bar max
  hold, 1% risk/trade, 3x leverage

Parameters: n=10, roc=10, trigger=5.0, sma50. WARMUP=70.

Usage:

```python
from strategies.data import fetch_candles
from strategies.chaikin_volatility import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))  # trigger=5.0 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the trigger=2.5/5.0/10.0 sensitivity check.

Sources: Chaikin Volatility —
https://www.spread-betting.com/trader-training/chaikin-volatility-oscillator
and https://www.fmz.com/strategy/461363 (Chaikin Volatility +
MA trend strategy)
