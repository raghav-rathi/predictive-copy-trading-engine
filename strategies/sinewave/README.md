# SineWave

John F. Ehlers' SineWave indicator (*Cybernetic Analysis for Stocks
and Futures*, 2004; TA-Lib `HT_SINE`): the Hilbert transform of
detrended median price gives the instantaneous cycle phase, and the
indicator plots that phase as two lines — the sine of the phase and
the sine of the phase advanced 45 degrees. The two lines cross near
cycle turning points. In cycle mode the lines oscillate and the
crosses mark turns; in trend mode they go out of sync and stop
crossing usefully — Ehlers' own caveat, and exactly what the 1h
crypto backtest shows.

## Rules

- **Long entry:** SineWave crosses above LeadSine.
- **Short entry:** SineWave crosses below LeadSine.
- **Long exit / reverse:** SineWave crosses below LeadSine.
- **Short exit / reverse:** SineWave crosses above LeadSine.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail as the exit mechanism
  plus the opposite cross. Max hold 120 bars.
- Distinct from `ehlers_sinewave`, which is the "Even Better
  Sinewave" approximation (sine = wave / sqrt(pwr) with a
  slope-extrapolated lead). Here the phase comes from a real FIR
  Hilbert transformer: SineWave = sin(phase), LeadSine =
  sin(phase + 45 deg).

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- John F. Ehlers, *Cybernetic Analysis for Stocks and Futures* (2004), and *Rocket Science for Traders* (2001): https://ta-lib.org/functions/ht_sine.html

Paper only, no live execution.
