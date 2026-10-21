# Stochastic RSI

Chande & Kroll's momentum oscillator: apply the stochastic formula
to RSI itself instead of price, so it reacts faster to momentum
extremes than raw RSI. %K leaving the 20/80 zones marks exhaustion —
the trigger is the *exit* from the extreme zone, not the extreme
itself.

- **Long:** %K crosses above 20 (momentum leaves the oversold zone —
  downside exhaustion)
- **Short:** %K crosses below 80 (momentum leaves the overbought
  zone — upside exhaustion)
- **Exit:** %K crosses the 50 midline (the bounce leg is done)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max hold,
  1% risk/trade, 3x leverage

Parameters: RSI(14), stochastic window 14, %K = SMA(3), %D = SMA(3)
(computed, unused by signals — %K alone is the trigger), ATR(14)
for stop/trail.

Usage:

```python
from strategies.data import fetch_candles
from strategies.stoch_rsi import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=240)
sig = signals.add_signals(indicators.add_indicators(df))  # (14,14,3,3) defaults
```

See BACKTEST.md for the 2026-03-14 → 2026-10-21 Hyperliquid 1h
(BTC/ETH/HYPE) results — honest verdict: loser, BTC leg
catastrophic — and CALIBRATION.md for the (2,2)/(3,3)/(5,5)
smoothing sensitivity check.
