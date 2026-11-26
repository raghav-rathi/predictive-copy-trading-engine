# Donchian Stochastic

Richard Donchian's channel breakout with a Stochastic
(14,3,3) filter, and the classic Turtle exit plus a momentum
exit. The channel is the highest high and lowest low of the
last 20 periods; a close above the prior 20-bar high is a
long, below the prior 20-bar low a short — but only when the
Stochastic agrees (long: %K > %D and %K < 80; short: %K < %D
and %K > 20). The exit is the 10-bar Turtle channel, or a
%K/%D cross against the position.

- **Long:** close crosses above the prior 20-bar Donchian high
  AND %K > %D AND %K < 80
- **Short:** close crosses below the prior 20-bar Donchian low
  AND %K < %D AND %K > 20
- **Exit:** long exits when the close falls below the prior
  10-bar Donchian low OR %K crosses below %D; short exits
  when the close rises above the prior 10-bar Donchian high
  OR %K crosses above %D
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 120-bar
  max hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the Turtle/momentum exit as a safety net for
  gap-through moves)

Parameters: entry channel 20 bars, exit channel 10 bars,
Stochastic(14,3,3) with long max 80 / short min 20. Both
channels are judged against the prior bars (shifted by 1) —
the breakout is vs the prior 20 bars, never the current
bar's own high or low. The exit shift is required, not
optional: the unshifted 10-bar low includes the current
bar's own low, and the close can never be below it, so the
unshifted exit could never fire. ATR(14) in the harness for
the stop/trail.

Note on the filter: a breakout close sits at the extreme of
its 14-bar range, so %K is near 100 on a long breakout and
near 0 on a short breakdown — the %K < 80 / > 20 gates only
pass when the breakout bar carries a real wick (high well
above the close, or low well below it). On tight-spread
synthetic data the filter blocks nearly every breakout; on
real 1h bars it passes rarely, which is why this system
trades far less than the unfiltered Donchian combo (61
trades vs 536 for donchian_rsi_combo on the same window).

Source: Richard Donchian — Donchian channel —
https://en.wikipedia.org/wiki/Donchian_channel; Stochastic
oscillator (George Lane) —
https://en.wikipedia.org/wiki/Stochastic_oscillator (%K =
100×(close − lowest low)/(highest high − lowest low),
%D = SMA(%K, 3), 80/20 overbought/oversold levels).

Usage:

```python
from strategies.donchian_stochastic import indicators, signals, risk

df = indicators.add_indicators(df)  # entry_n=20, exit_n=10 defaults
sig = signals.add_signals(df)  # k_overbought=80.0, k_oversold=20.0 defaults
```

See BACKTEST.md for the 2026-03-14 → 2026-11-26 Hyperliquid 1h
(BTC/ETH/HYPE, batch-47 pinned window) results and
CALIBRATION.md for the entry-window 10/20/55 sensitivity
check.
