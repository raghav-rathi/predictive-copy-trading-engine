# Ehlers Universal Oscillator

John F. Ehlers' adaptive band-pass oscillator from "Cycle
Analytics for Traders" (2013) — the same two-pole resonator
as the dominant-cycle meter, but as a trading oscillator:
median price ((h+l)/2) through a tighter resonator (period
20, bandwidth 0.3), AGC-normalized by its rolling 100-bar
RMS, with a trigger line of the normalized output delayed
one bar and scaled 0.9 (Ehlers' adaptive band-pass trigger
convention).

- **Long:** normalized band-pass output crosses above the
  trigger line
- **Short:** normalized band-pass output crosses below the
  trigger line
- **Exit:** the opposite cross (long exits on a cross below
  the trigger, short on a cross above)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 120-bar
  max hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the trigger-cross exit as a safety net)

Parameters: resonator period 20, bandwidth 0.3; AGC RMS
window 100 bars (expanding until 100 bars accumulate, so the
output is defined from the first bar); trigger scale 0.9.
Divide-by-zero is guarded: when the RMS is 0 the normalized
output is 0. ATR(14) in the harness for the stop/trail.

Source: John F. Ehlers — "Cycle Analytics for Traders" (2013),
band-pass filter chapter —
https://www.tradingview.com/script/jtvNFAgS-Ehlers-Band-Pass-Filter/

Usage:

```python
from strategies.ehlers_universal_osc import indicators, signals, risk

df = indicators.add_indicators(df)  # period=20, bandwidth=0.3 defaults
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-26 Hyperliquid 1h
(BTC/ETH/HYPE, batch-47 pinned window) results and
CALIBRATION.md for the trigger-scale sensitivity check.
