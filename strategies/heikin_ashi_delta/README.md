# Heikin Ashi Delta Momentum

Momentum-turn entries on the Heikin Ashi delta — the sign of
(HA_close − HA_open) is the Heikin Ashi candle colour.

- **HA_close** = (o + h + l + c) / 4
- **HA_open** = (prev HA_open + prev HA_close) / 2 (seeded with the
  first bar's open)
- **delta** = HA_close − HA_open
- **Long:** delta crosses from negative to positive (or turns positive
  after ≥ 3 negative bars) with HA_close > HA_open
- **Short:** delta crosses from positive to negative (or turns
  negative after ≥ 3 positive bars) with HA_close < HA_open
- **Exit:** delta crosses back through zero
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 150-bar max hold,
  1% risk/trade, 3x leverage

Parameters: none tunable in the formula itself (the HA recursion is
fixed); ATR(14) for stop/trail. WARMUP=60.

Usage:

```python
from strategies.data import fetch_candles
from strategies.heikin_ashi_delta import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the (no-parameter) calibration note.

Source: Heikin Ashi trading strategy —
https://www.babypips.com/learn/forex/how-to-trade-heikin-ashi?locale=ja

## Honest caveats

- **Heikin Ashi smoothing lag is the central limitation.** Each
  HA_open is an average of the previous HA candle, so the delta sign
  change that triggers an entry arrives several bars after the real
  price turn — entries chase moves that have already started, and
  exits come after the reversal is already underway. On 1h crypto
  this produced a zero-cross roughly every 8 bars and a 24–31% win
  rate (see BACKTEST.md).
- HA prices are averages, not real prices: HA_close differs from the
  market close, so all order levels (stop, trail, entry) are set from
  real OHLC, never from HA values.
- The delta zero-cross is a pure momentum-turn signal with no trend
  filter: in range-bound chop it flips constantly and bleeds fees
  (fees were $15,130 across the three coins in the batch window).
- Single 7-month crypto window; results are paper-only, funding
  unmodeled, next-bar-open execution.
