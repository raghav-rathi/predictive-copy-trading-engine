# Spinning Top

Steve Nison's spinning top — a small body with long wicks on
both sides, indecision made visible — traded as a reversal
only when it prints at a swing extreme: at a swing low it
reads as selling exhaustion, at a swing high as buying
exhaustion.

- **Long:** a spinning top (body ≤ 30% of the range, each wick
  ≥ 30% of the range) whose low reaches the lowest low of the
  prior 20 bars
- **Short:** a spinning top whose high reaches the highest high
  of the prior 20 bars
- **Exit:** the opposite signal (a spinning top at the opposite
  extreme)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage

Parameters: swing lookback 20 bars, body ≤ 30% / wicks ≥ 30%
of the bar's range, ATR(14) for stop/trail.

Usage:

```python
from strategies.spinning_top import indicators, signals, risk

df = indicators.add_indicators(df)  # swing_lookback=20 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-24 Hyperliquid 1h
(BTC/ETH/HYPE) results — honest verdict: loser on all three
coins (combined -$4,049.12 on 292 trades) — and CALIBRATION.md
for the 10/20/40 swing-lookback sensitivity check.
