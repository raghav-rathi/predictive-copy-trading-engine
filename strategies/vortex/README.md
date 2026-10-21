# Vortex Indicator Crossover

Trend-regime cross on the Vortex Indicator (Botes & Siepman, TASC
January 2010).

- **VM+** = |h − l.shift(1)|, **VM−** = |l − h.shift(1)|
- **VI+(14)** = sum14(VM+) / sum14(TR), **VI−(14)** = sum14(VM−) / sum14(TR)
- **Long:** VI+ crosses above VI− (buying pressure takes the lead in
  the 14-bar window)
- **Short:** VI+ crosses below VI−
- **Exit:** the opposite cross — the strategy always rides whichever
  line is on top
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 120-bar max hold,
  1% risk/trade, 3x leverage

Parameters: n=14, ATR(14) for stop/trail. WARMUP=60.

Usage:

```python
from strategies.data import fetch_candles
from strategies.vortex import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))  # n=14 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the n=10/14/20 sensitivity check.

Source: Vortex Indicator (Botes & Siepman) —
https://www.investopedia.com/terms/v/vortex-indicator-vi.asp
