# Williams %R Divergence

Larry Williams' %R divergence: %R(14) = -100 * (highest
high(14) − close) / (highest high(14) − lowest low(14)),
read for regular divergence against price on confirmed
±2-bar pivots — the same pivot machinery as
strategies/macd_rsi_divergence, followed exactly.

- **Long:** bullish divergence confirmed — price makes a
  lower low on a confirmed pivot while %R makes a higher
  low, with %R < −80 at the pivot; long on the close of the
  confirming bar (executed at next-bar open by the harness)
- **Short:** bearish divergence confirmed — price higher
  high, %R lower high, %R > −20 at the pivot
- **Exit:** %R crosses back through −50 against the
  position (long exits on a cross below −50, short on a
  cross above −50), or on the opposite divergence
- **Risk:** 2xATR hard stop, 3xATR chandelier trail,
  120-bar max hold, 1% risk/trade, 3x leverage (the harness
  stops sit behind the %R exit as a safety net for
  gap-through moves)

A confirmed pivot low is a bar whose low is the strict
lowest low of the ±2-bar window around it; the pivot bar is
i−2 and bar i is the confirmation bar, so the signal is only
available at bar i (two bars of confirmation). Entries are
transition-only via a state machine: a signal fires only
when flat (or on a flip bar), and while a position is held
repeated divergence bars do NOT re-enter. An exit on a bar
that also carries the opposite entry condition flips the
position. Divergence needs two pivots by construction, so
entries lag the turn by design.

Parameters: %R(14), pivot half-window 2, divergence gates
−80 / −20, exit level −50. Where the 14-bar range is 0
(a flat bar) %R reads −50, the neutral value.

Source: Larry Williams — Williams %R divergence —
https://en.wikipedia.org/wiki/Williams_%R

Usage:

```python
from strategies.williams_r_divergence import indicators, signals, risk

df = indicators.add_indicators(df)  # wr_n=14 defaults
sig = signals.add_signals(df)  # exit_level=-50.0 default
```

See BACKTEST.md for the 2026-03-14 → 2026-11-26 Hyperliquid 1h
(BTC/ETH/HYPE, batch-47 pinned window) results and
CALIBRATION.md for the %R-period 10/14/21 sensitivity
check.
