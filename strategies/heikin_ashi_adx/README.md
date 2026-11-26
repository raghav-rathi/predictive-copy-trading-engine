# Heikin Ashi ADX

Heikin Ashi candle colour with a Wilder ADX(14) trend filter.
A bullish HA bar (ha_close > ha_open) is only a long when the
trend is real — ADX(14) > 25 — and points up (+DI > −DI). A
bearish HA bar is only a short when ADX > 25 and −DI > +DI.
The exit is the HA bar flipping against the position, or ADX
falling below 20 (the trend has died).

- **Long:** HA bullish bar AND ADX(14) > 25 AND +DI > −DI
- **Short:** HA bearish bar AND ADX(14) > 25 AND −DI > +DI
- **Exit:** long exits on a bearish HA bar or ADX < 20; short
  exits on a bullish HA bar or ADX < 20
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 120-bar
  max hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the HA-flip exit as a safety net for gap-through
  moves)

Parameters: ADX(14) with entry threshold 25 / exit threshold
20; HA recursion seeded with the first real open. Entries are
level conditions, not crosses: while the trend persists the
signal stays true, and the harness (one position at a time,
flat between trades) takes the first bar after going flat.
Stops are computed on REAL prices, never on HA values.
ATR(14) in the harness for the stop/trail.

Source: Heikin-Ashi chart —
https://en.wikipedia.org/wiki/Heikin-Ashi_chart (HA formulas:
ha_close = (o+h+l+c)/4, ha_open = midpoint of the previous
HA open/close, ha_high/low the envelope of h/l and the HA
open/close); ADX/+DI/−DI are J. Welles Wilder's (1978).

Usage:

```python
from strategies.heikin_ashi_adx import indicators, signals, risk

df = indicators.add_indicators(df)  # adx_n=14 default
sig = signals.add_signals(df)  # adx_entry=25.0, adx_exit=20.0 defaults
```

See BACKTEST.md for the 2026-03-14 → 2026-11-26 Hyperliquid 1h
(BTC/ETH/HYPE, batch-47 pinned window) results and
CALIBRATION.md for the ADX-threshold 20/25/30 sensitivity
check.
