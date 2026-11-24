# Fakey

Nial Fuller's Fakey — a false break of an inside bar. A mother
bar sets the range, an inside bar coils within it, and the next
bar pokes outside the inside bar only to close back inside the
mother bar's range. The false break traps breakout traders on the
wrong side; the trade runs in the direction of the failed break.

- **Long:** bar i breaks BELOW the inside bar's low (low[i] <
  low[i-1]) but closes back inside the mother bar's range
  (close[i] > low[i-2])
- **Short:** bar i breaks ABOVE the inside bar's high (high[i] >
  high[i-1]) but closes back inside the mother bar's range
  (close[i] < high[i-2])
- **Exit:** the opposite signal (the range has now genuinely
  broken the other way)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max hold,
  1% risk/trade, 3x leverage

Parameters: mother bar i-2, inside bar i-1, break/close bar i;
confirmation = close back inside the mother bar's range
(shipped). A bar that breaks BOTH sides of the inside bar while
closing inside the mother range is ambiguous and fires neither
entry.

Usage:

```python
from strategies.data import fetch_candles
from strategies.fakey import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=240)
sig = signals.add_signals(indicators.add_indicators(df))  # confirm="mother" default
```

See BACKTEST.md for the 2026-03-14 → 2026-11-24 Hyperliquid 1h
(BTC/ETH/HYPE, batch-45 window) results — honest verdict: loser
on all three coins, combined -$9,434.01 — and CALIBRATION.md for
the mother-range vs inside-range confirmation check.
