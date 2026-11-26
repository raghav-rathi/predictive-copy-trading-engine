# The Strat

Rob Smith's The Strat: every bar is classified against the
prior bar — 1 (inside), 2U (breaks the prior high only), 2D
(breaks the prior low only), 3 (outside, breaks both) — and
trades are taken on the classic three-bar setups. Every setup
is gated by full time frame continuity (FTFC): longs only
when the daily AND weekly directions are both green, shorts
only when both are red.

- **Long:** 2-1-2 reversal (2D, 1, 2U), 3-1-2 reversal
  (3, 1, 2U), 2-2 reversal (2D, 2U), or 2-1-2 continuation
  (2U, 1, 2U) — with daily AND weekly FTFC green
- **Short:** the mirror images — with daily AND weekly FTFC
  red
- **Exit:** a long exits on any short setup, a short on any
  long setup (the Strat's own reversal is the exit; the exit
  is NOT FTFC-gated)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 120-bar
  max hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the signal exit as a safety net)

Parameters: daily FTFC from 24-bar blocks, weekly FTFC from
168-bar blocks; a block's direction is its last close minus
its first open, applied only to bars after the block
completes. The entry signal fires on the close of the trigger
bar (the final 2 bar) and the harness enters at the next
bar's open — the close-based adaptation of the book's
trigger-break entry (a stop order above/below the 2 bar),
which cannot be executed on 1h close bars. Equal highs/lows
fall on the inside side of the boundary, so the four classes
partition every bar. ATR(14) in the harness for the
stop/trail.

Source: Rob Smith — The Strat —
https://www.luxalgo.com/library/concept/the-strat/ and
https://www.smoothstrat.com/course.html

Usage:

```python
from strategies.the_strat import indicators, signals, risk

df = indicators.add_indicators(df)  # daily_bars=24, weekly_bars=168 defaults
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-26 Hyperliquid 1h
(BTC/ETH/HYPE, batch-47 pinned window) results and
CALIBRATION.md for the FTFC-gate sensitivity check.
