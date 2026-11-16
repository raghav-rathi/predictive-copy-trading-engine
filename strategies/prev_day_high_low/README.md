# Prior Day High/Low Breakout

Session-structure breakout: stop orders cluster above the prior
session's high and below its low, so a close through the level is
treated as a breakout. Crypto trades 24/7 with no true session close,
so the UTC day is the adopted session boundary.

- **Long:** 1h close above the prior UTC-day high + 0.1% filter
- **Short:** 1h close below the prior UTC-day low − 0.1% filter
- **Skip:** days whose prior-day range is < 0.5x its 20-day median
  (narrow-range days whipsaw)
- **Exit:** 1h close back inside the prior-day range, the opposite
  level breaking, or UTC midnight flat (first bar of a new UTC day)
- **Risk:** 1.5xATR stop (≈ just inside the broken level — see
  risk.py), 3xATR target (2R), 24-bar max hold, 1% risk/trade,
  3x leverage

Parameters: filter 0.1%, range filter 0.5x 20-day median. WARMUP=48.

Execution note: the midnight-flat exit is generated on the first bar
of the new UTC day and the harness executes it at the *next* bar's
open, so the position is flat one bar into the new day rather than
exactly at midnight.

Usage:

```python
from strategies.data import fetch_candles
from strategies.prev_day_high_low import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the filter sensitivity check.

Source: PDH/PDL breakout —
https://www.quantsapp.com/backtesting/strategies/pdh-pdl-breakout-futures-and-option-buy

## Honest caveats

- The UTC-day boundary is arbitrary for a 24/7 market, and the batch
  window says so: combined -$7,046 on 604 trades, red on all three
  coins with win rates under 31%. Breakouts of an arbitrary level
  fail back inside the range more often than they run.
- The range filter cuts the worst narrow days but does not cure the
  whipsaw: 604 trades in 8 months is roughly 2.5 breakouts a day
  across three coins, and ~70% of them lose.
- Single 8-month crypto window; no out-of-sample evidence.
