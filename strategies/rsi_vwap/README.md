# RSI + Session VWAP

RSI(14) momentum timing against the day's session VWAP:
buy the oversold bounce only while price is above the
day's value area, sell the overbought fade only while
price is below it. The VWAP side is the trend/value
filter; the RSI cross is the timing trigger.

- **Long:** RSI(14) crosses up through 30 while the close
  is above the session VWAP
- **Short:** RSI(14) crosses down through 70 while the
  close is below the session VWAP
- **Exit:** RSI crosses 50 against the position (long exits
  on RSI crossing below 50; short on RSI crossing above 50)
  OR the close crosses the session VWAP against the
  position (long exits on a close below VWAP; short on a
  close above VWAP)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 120-bar
  max hold, 1% risk/trade, 3x leverage

Parameters: RSI(14), oversold 30 / overbought 70, exit
midline 50. The session VWAP is anchored at the UTC-day
boundary (00:00 UTC), computed from typical price
(h + l + c) / 3 weighted by volume, resetting each UTC day
-- the exact construction of `vwap_session_breakout`
(same cumulative-sum form). On the first bar of a session
VWAP equals that bar's typical price, so the close cannot
be meaningfully above or below it and no signal can fire
there. Note the house-rule caveat: `base.rsi` 0-fills on
flat stretches (a flat run prints RSI 0 after a rise, 100
after a fall); WARMUP = 40 suppresses the spin-up, and the
first defined RSI bar can jump 0 -> 100, which registers as
a cross -- inside warmup only, the harness never trades it.

Source: RSI + session VWAP (standard combination;
session-VWAP convention per `vwap_session_breakout`) --
https://en.wikipedia.org/wiki/Relative_strength_index

Usage:

```python
from strategies.rsi_vwap import indicators, signals, risk

df = indicators.add_indicators(df)  # rsi_n=14 default
sig = signals.add_signals(df)  # rsi_oversold=30.0, rsi_overbought=70.0 defaults
```

See BACKTEST.md for the 2026-03-14 → 2026-11-26 Hyperliquid 1h
(BTC/ETH/HYPE, batch-47 pinned window) results and
CALIBRATION.md for the RSI-level 20/80, 30/70, 40/60
sensitivity check.
