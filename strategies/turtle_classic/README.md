# Original Turtle Rules

Richard Dennis and William Eckhardt's Turtle system (published 2003 by
Curtis Faith, one of the original Turtles), adapted from **daily to 1h
bars** — the original 20/55/10/20-day lookbacks become 20/55/10/20-bar
lookbacks. Stated plainly: this is a timeframe adaptation, not the
original system.

## Rules

- **System 1 entry:** long when the close breaks above the 20-bar
  Donchian high, short below the 20-bar low.
  **Skip rule:** a System-1 signal is skipped when the previous
  *completed* System-1 trade in the same direction was a winner.
- **System 2 entry (failsafe):** long/short on the 55-bar Donchian
  breakout, taken only when flat and the last System-1 signal in the
  same direction was skipped — always taken once those hold.
- **Exits:** System-1 positions exit on the 10-bar opposite-channel
  cross; System-2 on the 20-bar cross.
- **Stop:** 2N = 2 × ATR(20) from entry (the Turtles' "N").
- **Risk:** 1% equity risk per trade on the 2N stop, 3x leverage cap,
  500-bar max-hold guardrail. **No pyramiding** — the original added a
  unit every 0.5N up to 4 units; this build trades a single unit per
  position, one position at a time, by design.

Execution: entry channels are shifted by 1 so a breakout bar's close
triggers the entry; the harness executes at the next bar's open.
Columns: `long_entry/short_entry/long_exit/short_exit` (merged),
`long_entry_s1/.../long_entry_s2/...` per-system entries, and a
`system` tag (`'S1'`/`'S2'` on entry bars).

Parameters: entry 20 / failsafe 55 / S1 exit 10 / S2 exit 20 /
ATR(20). WARMUP=120.

Usage:

```python
from strategies.turtle_classic import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the S1-only entry-channel sensitivity check.

Sources:

- The Original Turtle Trading Rules (Curtis Faith, 2003) —
  http://mql5.com/en/articles/23448
- Turtle Trading Rules: Does the Original Strategy Still Work? —
  https://relaxedtrader.com/original-turtle-trading-rules/
