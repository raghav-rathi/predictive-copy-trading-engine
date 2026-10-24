# Ehlers Roofing Filter — Calibration

All parameters were fixed **a priori** from Ehlers' published
Roofing Filter specification and 1h-bar reasoning — there is no
in-sample sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| High-pass cycle | 48 | Ehlers' canonical roofing cycle; 48h = 2 days on 1h bars, a plausible crypto swing-cycle length |
| SuperSmoother period | 10 | Ehlers' standard smoothing length for the roofing output — short enough not to re-lag the cycle estimate |
| ATR window | 14 | canonical |
| Stop | 1.5xATR | standard for a fast cycle-turn entry |
| Trail | 2xATR chandelier | rides the cycle leg that extends |
| Max hold | 72 bars (~3 days) | ~1.5 tuned cycles; a cycle turn that hasn't resolved in that time was not a cycle turn |
| Risk | 1% / trade, 3x leverage cap | house standard |

The design bet is that the roofing line's zero crossings time
cycle turns better than a moving-average cross. The backtest
(BACKTEST.md) rejects that bet on 1h crypto bars: the crossings
fire ~500 times per coin and mostly stop out.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers.
