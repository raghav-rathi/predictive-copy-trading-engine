# Holy Grail

Linda Raschke's Holy Grail setup from *Street Smarts* (with Larry
Connors): buy the first pullback to the average in a strong,
strengthening trend.

- **Regime:** close on the trend side of EMA(20) **and** ADX(14) >
  30 **and** ADX rising
- **Touch bar:** low (high) tags the EMA(20) but the close holds the
  trend side
- **Long entry:** next bar closes above the touch bar's high
  (simulated buy-stop). **Short:** mirror image below the touch low
- **Exit:** close back through the average, or ADX falls under 20
  (the trend faded)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 100-bar max
  hold, 1% risk/trade, 3x leverage

Parameters: EMA(20), ADX(14) entry threshold 30, ADX exit 20, ATR(14)
for stop/trail.

Usage:

```python
from strategies.data import fetch_candles
from strategies.lbr_holy_grail import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=240)
sig = signals.add_signals(indicators.add_indicators(df))  # adx_thresh=30 default
```

See BACKTEST.md for the 2026-03-14 → 2026-10-21 Hyperliquid 1h
(BTC/ETH/HYPE) results — **15 trades total, no evidence of edge** —
and CALIBRATION.md for the 25/30/35 ADX-threshold sensitivity check.
