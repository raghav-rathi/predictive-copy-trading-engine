# UT Bot Alerts

QuantNomad's UT Bot Alerts (original idea HPotter) — an ATR
trailing stop that flips sides, and the flip is the trade.
Heikin Ashi is OFF: the stop runs on raw closes.

- **Long:** close crosses above the trailing stop (the stop
  flips from above price to below it)
- **Short:** close crosses below the trailing stop
- **Exit:** the opposite signal — the stop flipping back is
  the trend change
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the UT stop itself as a safety net for gap-through
  moves)

Parameters: ATR(10) (Wilder), KeyValue 1.0 — the stop sits
KeyValue × ATR(10) away from price. ATR(14) in the harness
for the stop/trail.

Usage:

```python
from strategies.ut_bot import indicators, signals, risk

df = indicators.add_indicators(df)  # key_value=1.0 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-24 Hyperliquid 1h
(BTC/ETH/HYPE, batch-45 pinned window) results — honest verdict:
the worst loser of this batch by a wide margin — and
CALIBRATION.md for the KeyValue 1.0/2.0/3.0 sensitivity check
(re-run on the batch-45 window) and the refresh audit
(no lookahead, no bug found, source verified live).
