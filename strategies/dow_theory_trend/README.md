# Dow Theory Trend

Primary-trend trading on Dow Theory swing structure: higher highs and
higher lows define an uptrend, lower highs and lower lows a downtrend.

- **Pivots:** strict 5-bar pivots (2 bars each side), confirmed 2 bars
  after the extreme bar, so no lookahead
- **Trend:** HH + HL = uptrend; LH + LL = downtrend
- **Long:** uptrend confirmed, price pulls back 33–66% of the last
  up-leg (last swing high minus the swing low that preceded it), then
  a 1h close breaks above the last swing high with volume above its
  20-bar mean
- **Short:** mirror image (close below the last swing low after a
  33–66% pullback of the last down-leg)
- **Exit:** swing structure breaks (a new swing low under the previous
  swing low / a new swing high over the previous swing high), or the
  close retraces more than 66% of the leg
- **Risk:** 2xATR stop (≈ the last swing extreme — see risk.py), 4xATR
  target (2R), 120-bar max hold, 1% risk/trade, 3x leverage

Parameters: pivot_n=5, pullback band 33–66%, volume filter
vol_ratio > 1.0 (20-bar mean). WARMUP=60.

Usage:

```python
from strategies.data import fetch_candles
from strategies.dow_theory_trend import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the pivot-size sensitivity check.

Source: Dow Theory —
https://finabase.io/learn/technical-analysis/dow-theory

## Honest caveats

- Late by design: the trend only confirms after two full swing pairs,
  and the entry waits for a pullback plus a breakout, so the strategy
  buys legs that are already well under way. In the batch window that
  lateness costs more than it saves: combined -$2,009 on 262 trades.
- The volume filter is the single-asset substitute for Dow's
  cross-average confirmation; it is a weak filter (volume above its
  20-bar mean fires on most breakout bars) and does not rescue the
  entries.
- BTC and ETH are both clearly red (Sharpe -1.06 / -1.71); only HYPE
  is green (+$469), and that is one coin's luck, not a pattern.
- Single 8-month crypto window; no out-of-sample evidence.
