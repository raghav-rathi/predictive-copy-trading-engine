# Ehlers Roofing Filter

John Ehlers' Roofing Filter (Cycle Analytics): a high-pass filter
tuned to a 48-bar cycle, followed by a SuperSmoother. The roofing
line itself is the signal.

## The exact filters

High-pass stage, with alpha = 2*pi/48:

```
y[i] = (1 - alpha/2)^2 * (x[i] - 2*x[i-1] + x[i-2])
       + 2*(1 - alpha) * y[i-1] - (1 - alpha)^2 * y[i-2]
```

Seeded 0: y[0] = y[1] = 0. The high-pass removes trend and slow
drift, so the output oscillates around zero; its poles sit on the
48-bar cycle, so a 48-bar cyclic component passes with limited
attenuation (unit-tested: a pure 48-bar sine keeps ~47% of its
amplitude after smoothing) while slower components are rejected.

SuperSmoother stage (10-bar, Ehlers 2-pole coefficients):

```
a1 = exp(-1.414 * pi / 10)
b1 = 2 * a1 * cos(1.414 * 180 / 10)     (argument in degrees)
c2 = b1
c3 = -a1 * a1
c1 = 1 - c2 - c3
f[i] = c1 * (y[i] + y[i-1]) / 2 + c2 * f[i-1] + c3 * f[i-2]
```

Also seeded 0 for the first two bars. The smoother strips the
high-frequency noise the differentiator-style high-pass amplifies.
Unity DC gain (c1 / (1 - c2 - c3) == 1), so it does not rescale
the roofing line.

## Signals

The roofing line is detrended by construction, so its zero
crossings are cycle turns:

- LONG when the roofing line crosses above 0
- SHORT when it crosses below 0
- Exit on the opposite zero cross

No extra filters: the filter itself is the trend/cycle estimator,
and gating it would re-introduce the lag the Roofing Filter exists
to remove.

## Risk

1.5xATR stop, 2xATR chandelier trail, 72-bar (~3-day) max hold,
1% risk per trade, 3x leverage cap. WARMUP = 80 bars.

Source: John Ehlers, Cycle Analytics for Traders — Roofing Filter
(https://www.mesasoftware.com/).
