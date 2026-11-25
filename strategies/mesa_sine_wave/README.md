# MESA Sine Wave

John Ehlers' MESA Sine Wave — the Hilbert-transform cycle
indicator from "Cycle Analytics for Traders" / "Rocket Science
for Traders" ch. 12. The detrended price is split into
in-phase and quadrature components; their phase angle is the
cycle position, and the sine of the phase (plus a 45-degree
lead sine) is the trade trigger.

- **Long:** sine crosses above lead sine (cycle turning up
  near the bottom)
- **Short:** sine crosses below lead sine
- **Exit:** the opposite cross. "Lead sine crossing below
  sine" is the same event described from the other line, so
  the long and short entries are the two directions of one
  cross.
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the cross itself as a safety net for gap-through
  moves)

Parameters: 4-bar WMA smoother on hl2; Ehlers Hilbert
coefficients (0.0962/0.5769) for the detrender and the
quadrature filters; I2/Q2 smoothed 0.2/0.8; dominant cycle
from the homodyne discriminator, rate-limited, clamped
6..50 bars, smoothed 0.2/0.8; phase = atan2(Q2, I2);
sine = sin(phase), lead sine = sin(phase + pi/4). ATR(14)
in the harness for the stop/trail. WARMUP=120.

Usage:

```python
from strategies.mesa_sine_wave import indicators, signals, risk

df = indicators.add_indicators(df)  # smooth=0.2 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-25 Hyperliquid 1h
(BTC/ETH/HYPE, batch-46 pinned window) results — honest verdict:
the worst loser of this batch, a cycle-cross chop machine —
and CALIBRATION.md for the I2/Q2 smoothing 0.1/0.2/0.4
sensitivity check and the lookahead audit (no lookahead:
every value on bar i uses data through bar i's close only;
the homodyne period factor uses the previous bar's period).
