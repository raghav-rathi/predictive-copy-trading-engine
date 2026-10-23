# SMI Ergodic Oscillator Crossover

Zone-gated crossover of William Blau's SMI Ergodic Oscillator
("Momentum, Direction, and Divergence", 1995) with its 5-bar signal
line.

## Mechanism

Blau's SMI Ergodic is the same double-smoothed ergodic lineage as
the True Strength Index:

- **Momentum** m = close.diff()
- **SMI** = 100 × EMA(EMA(m, 5), 20) / EMA(EMA(|m|, 5), 20)
- **Signal** = EMA(SMI, 5)

The oscillator is a ratio of double-smoothed momentum to
double-smoothed absolute momentum, so it is exactly scale-invariant
and bounded in [-100, +100] (|EMA(m)| ≤ EMA(|m|) by the triangle
inequality). Blau's classic trade acts on crosses of the oscillator
with its signal line **from the extreme zones** (±40), not on
mid-band chop:

- **Long:** smi crosses above its signal while the prior-bar smi
  was at/below −40 (an oversold "hook" back up).
- **Short:** smi crosses below its signal while the prior-bar smi
  was at/above +40 (an overbought hook back down).
- **Exit:** the opposite cross — the momentum turn is the edge,
  so the cross back is the trade's own invalidation. No fixed
  target.

Parameters are Blau's published SMI Ergodic values, fixed a priori
with no in-sample selection: ergodic 5/20, signal 5, zones ±40
(see CALIBRATION.md).

- **Risk:** 1.5xATR hard stop, 2xATR chandelier trail, 96-bar
  (~4-day) max hold, 1% risk/trade, 3x leverage, symmetric
  long/short (Blau's oscillator is symmetric about zero, so
  overbought hooks short as legitimately as oversold hooks go
  long). WARMUP=120.

Usage:

```python
from strategies.smi_ergodic import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))  # Blau's 5/20/5/±40
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the parameter rationale.

## Sources

- William Blau lineage (same double-smoothed ergodic formula
  family; the TSI page documents the ergodic-ratio construction):
  https://en.wikipedia.org/wiki/True_strength_index
- TSI/ergodic explainer:
  https://www.gate.com/learn/articles/what-is-tsi-indicator

Honest note: the SMI Ergodic implementation above follows Blau's
book parameters (5/20 ergodic pair, 5-bar signal line, ±40
overbought/oversold zones) from "Momentum, Direction, and
Divergence" (1995). The Wikipedia TSI page documents the slower
25/13 TSI variant of the same ergodic family — it is cited for the
formula lineage, not as the source of the 5/20/5/±40 parameters.
