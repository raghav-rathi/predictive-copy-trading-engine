# Supertrend VWAP

Supertrend(10, 3.0) with a UTC-day session VWAP agreement
filter. A long needs both legs to agree: Supertrend is long
(direction +1, line below price) AND the close is above the
session VWAP. A short needs Supertrend short AND the close
below the session VWAP. Either leg turning against the
position exits it.

- **Long:** Supertrend direction +1 AND close > session VWAP
- **Short:** Supertrend direction −1 AND close < session VWAP
- **Exit:** long exits when Supertrend flips to −1 or the
  close falls below VWAP; short exits when Supertrend flips
  to +1 or the close rises above VWAP
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 120-bar
  max hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the flip/VWAP-cross exit as a safety net for
  gap-through moves)

Parameters: Supertrend ATR 10, multiplier 3.0 (the standard
defaults); session VWAP anchored at 00:00 UTC from typical
price (h+l+c)/3, volume-weighted, resetting each UTC day —
the same UTC-day anchor as vwap_session_breakout, via
base.anchored_vwap. Entries are level conditions, not
crosses: while both legs agree the signal stays true, and
the harness (one position at a time, flat between trades)
takes the first bar after going flat. ATR(14) in the harness
for the stop/trail.

Source: Supertrend indicator (Olivier Seban) —
https://www.investopedia.com/supertrend-indicator-7976167
(ATR bands around the bar midpoint with a one-way ratchet;
standard defaults ATR 10, multiplier 3).

Usage:

```python
from strategies.supertrend_vwap import indicators, signals, risk

df = indicators.add_indicators(df)  # st_n=10, st_k=3.0 defaults
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-26 Hyperliquid 1h
(BTC/ETH/HYPE, batch-47 pinned window) results and
CALIBRATION.md for the Supertrend-multiplier 2.0/3.0/4.0
sensitivity check.
