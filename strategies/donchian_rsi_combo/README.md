# Donchian RSI Combo

Richard Donchian's channel breakout with an RSI filter, and
the classic Turtle exit. The channel is the highest high and
lowest low of the last 20 periods; a close above the prior
20-bar high is a long, below the prior 20-bar low a short —
but only when RSI(14) is not already overextended. The exit
is the 10-bar Turtle channel: a long exits on a close below
the prior 10-bar low, a short on a close above the prior
10-bar high.

- **Long:** close crosses above the prior 20-bar Donchian high
  AND RSI < 70
- **Short:** close crosses below the prior 20-bar Donchian low
  AND RSI > 30
- **Exit:** long exits when the close falls below the prior
  10-bar Donchian low; short exits when the close rises above
  the prior 10-bar Donchian high
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 120-bar
  max hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the Turtle exit as a safety net for gap-through
  moves)

Parameters: entry channel 20 bars, exit channel 10 bars,
RSI(14) with long max 70 / short min 30. Both channels are
judged against the prior bars (shifted by 1) — the breakout
is vs the prior 20 bars, never the current bar's own high or
low. The exit shift is required, not optional: the unshifted
10-bar low includes the current bar's own low, and the close
can never be below it, so the unshifted exit could never
fire. ATR(14) in the harness for the stop/trail.

Source: Richard Donchian — Donchian channel —
https://en.wikipedia.org/wiki/Donchian_channel

Usage:

```python
from strategies.donchian_rsi_combo import indicators, signals, risk

df = indicators.add_indicators(df)  # entry_n=20, exit_n=10 defaults
sig = signals.add_signals(df)  # rsi_long_max=70.0, rsi_short_min=30.0 defaults
```

See BACKTEST.md for the 2026-03-14 → 2026-11-25 Hyperliquid 1h
(BTC/ETH/HYPE, batch-46 pinned window) results and
CALIBRATION.md for the entry-window 10/20/55 sensitivity
check.
