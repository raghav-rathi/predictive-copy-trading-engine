# Oops Gap Reversion

Larry Williams' Oops pattern: an opening gap against the prior day's
range is an overreaction, and the "oops" is satisfied when price
reverses back through the prior day's extreme — the buy stop just
above the prior day's low (or sell stop just below the prior day's
high) gets hit.

## 1h-crypto adaptation

Crypto trades 24/7 with no true opens, so a trading "day" is proxied
by a 24-bar session and a "gap" is a bar whose **open** prints beyond
the **completed prior session's** extreme:

- **prev_day_high** = rolling(24).max(high).shift(24)
- **prev_day_low** = rolling(24).min(low).shift(24)
- **gap_down** = open < prev_day_low (a fresh 24-bar breakdown at the open)
- **gap_up** = open > prev_day_high

The shift(24) keeps the range strictly in the completed session — no
lookahead. Honest caveat: on 1h crypto bars these "gaps" are really
breakdown/breakout opens, and they are rarer than equity opening gaps.

## Rules

- **Long:** the first bar within 24 bars of a gap_down bar whose
  **close** is back above *that gap bar's* prev_day_low. The stop
  level is pinned at the gap bar's prior-session low, like Williams'
  fixed buy stop.
- **Short:** the mirror — first close back below the gap bar's
  prev_day_high within 24 bars of a gap_up bar.
- **One entry per gap** (the stop triggers once); if price never
  reclaims the pinned extreme within 24 bars, the setup expires.
- **Exit:** the opposite Oops signal, or the session clock running
  out — max_hold_bars=24 flattens the position, matching Williams'
  intraday flat-by-close design.
- **Risk:** 1.5xATR hard stop, no trail, no target, 1% risk/trade,
  3x leverage. WARMUP=48.

Usage:

```python
from strategies.oops_pattern import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))  # session=24 default
res = run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                   use_funding=False)
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the session=12/24/48 sensitivity check.

Source: Oops Pattern (Larry Williams) —
https://tr.tradingview.com/chart/AMZN/jING0osQ-The-OOPS-Pattern/
