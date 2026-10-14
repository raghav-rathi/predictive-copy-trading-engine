# Klinger Volume Oscillator — Calibration

**Shipped:** KVO = EMA(VF,34)−EMA(VF,55), 13-EMA signal, cross entries,
2.5xATR stop, 3xATR trail.

**What the numbers say:** −$9,971 combined over 1,742 trades — the
cross fires every ~8 bars on BTC. Win rate 29.9% with PF 0.62 means
the signal has no edge at this frequency; costs do the rest. Volume
force on 1h perps is chop-volume, not accumulation flow.

**Next experiment (only if revisited):** daily bars. Klinger's
original work was daily equities; the dm/cm temp term assumes
institutional-scale volume distribution across the bar range. On 1h
there is no version of this that works — the signal/noise ratio is
the problem, not the parameters.

**Do not:** tune 34/55/13 — with 1,742 trades the loss is not a
parameter artifact.
