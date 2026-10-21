# Elder Triple Screen

Alexander Elder's Triple Screen from *Trading for a Living* (1993):
three screens, each filtering the last.

- **Screen 1 — the tide (6h):** 1h bars resampled to 6h (o=first,
  h=max, l=min, c=last, v=sum); MACD(12,26,9) on the 6h closes.
  `trend_up_6h` = histogram > 0 and rising; `trend_down_6h` =
  histogram < 0 and falling. Each 1h bar reads the last 6h bar that
  fully closed at or before its open — no lookahead.
- **Screen 2 — the wave (1h):** Force Index = `(c - c[1]) * v`,
  smoothed to EMA(2).
- **Long:** tide up **and** the wave crosses back below zero
  (buy the pullback). **Short:** tide down **and** the wave crosses
  back above zero.
- **Exit:** the trend screen flips — Elder's exit rule (the tide
  turned, the trade is over).
- **Risk:** 2.5xATR hard stop, 3.5xATR chandelier trail, 150-bar max
  hold, 1% risk/trade, 3x leverage. Screen 3's intraday stop-entry
  precision is approximated by next-bar-open execution.

Parameters: 6h MACD(12,26,9), 1h Force Index EMA(2), ATR(14) for
stop/trail.

Usage:

```python
from strategies.data import fetch_candles
from strategies.elder_triple_screen import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=240)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the 2026-03-14 → 2026-10-21 Hyperliquid 1h
(BTC/ETH/HYPE) results — **loser on all three coins, do not ship
live** — and CALIBRATION.md for the 6h MACD speed sensitivity check
(all settings lose).
