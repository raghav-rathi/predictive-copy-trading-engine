# Ehlers Dominant Cycle

John F. Ehlers' band-pass resonator from "Cycle Analytics for
Traders" (2013), used as a cycle-trading oscillator. The close
is first detrended with Ehlers' one-pole high-pass filter
(cutoff one octave below the half-bandwidth edge of the pass
band), then passed through the two-pole band-pass resonator
(centre period 20, bandwidth 0.7 — an octave-wide pass band).
The dominant cycle period — twice the bars between successive
band-pass zero crossings, SMA-10 smoothed, clamped to
[6, 50] — is reported as a diagnostic.

- **Long:** band-pass output crosses above zero
- **Short:** band-pass output crosses below zero
- **Exit:** the opposite cross (long exits on a cross below
  zero, short on a cross above)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 120-bar
  max hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the zero-cross exit as a safety net)

Parameters: resonator period 20, bandwidth 0.7; high-pass
cutoff period 61.5 bars (lower pass-band edge 20 / (1 - 0.7/2)
= 30.8 bars, one octave below = 61.5); dominant-cycle SMA 10,
clamp [6, 50]. The dominant-cycle column is diagnostic only —
it does not gate or size trades. ATR(14) in the harness for
the stop/trail.

Source: John F. Ehlers — "Cycle Analytics for Traders" (2013),
band-pass filter / dominant-cycle measurement chapter —
https://docs.wickra.org/Indicators/Indicator-BandpassFilter

Usage:

```python
from strategies.ehlers_dominant_cycle import indicators, signals, risk

df = indicators.add_indicators(df)  # period=20, bandwidth=0.7 defaults
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-26 Hyperliquid 1h
(BTC/ETH/HYPE, batch-47 pinned window) results and
CALIBRATION.md for the bandwidth sensitivity check.
