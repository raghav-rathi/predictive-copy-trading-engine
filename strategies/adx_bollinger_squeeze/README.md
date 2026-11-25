# ADX Bollinger Squeeze

Bollinger Bands (20, 2.0) compress into a squeeze — bandwidth
at its 20-bar minimum — and the trade is the expansion that
follows, taken only when ADX(14) says a real trend is behind
it. The squeeze itself carries no direction; the breakout
side and the ADX filter pick it.

- **Long:** a squeeze was true within the last 3 bars AND the
  close crosses above the upper Bollinger Band AND ADX > 20
- **Short:** a squeeze was true within the last 3 bars AND the
  close crosses below the lower Bollinger Band AND ADX > 20
- **Exit:** the close crosses back inside the bands (long:
  below the upper band; short: above the lower band) OR
  ADX falls below 15
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the signal exit as a safety net for gap-through-band
  moves)

Parameters: BB(20, 2.0), bandwidth = (upper − lower) / mid,
squeeze = bandwidth at its 20-bar minimum, ADX(14) entry
threshold 20, ADX exit threshold 15, squeeze lookback 3 bars.
ATR(14) in the harness for the stop/trail.

Source: John Bollinger — Bollinger Bands / Bandwidth squeeze —
https://www.nasdaq.com/articles/rare-volatility-indicator-helps-spot-price-breakouts-2019-04-15

Usage:

```python
from strategies.adx_bollinger_squeeze import indicators, signals, risk

df = indicators.add_indicators(df)  # bb_n=20, bb_k=2.0 defaults
sig = signals.add_signals(df)  # adx_entry=20.0, adx_exit=15.0 defaults
```

See BACKTEST.md for the 2026-03-14 → 2026-11-25 Hyperliquid 1h
(BTC/ETH/HYPE, batch-46 pinned window) results and
CALIBRATION.md for the ADX-threshold 15/20/25 sensitivity
check.
