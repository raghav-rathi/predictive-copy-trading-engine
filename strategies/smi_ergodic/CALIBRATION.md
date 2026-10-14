# SMI Ergodic — Calibration

**Shipped:** SMI = 100·EMA(EMA(d,20),5)/EMA(EMA(|d|,20),5), 5-bar signal,
cross entries with zero-line regime filter, 2xATR stop, 3xATR trail.

**What the numbers say:** −$7,736 combined, worst expectancy in the
batch (−$8.45/trade). The zero-line filter was supposed to cut
counter-trend whipsaw; instead it delayed entries into extended moves
— expectancy is negative on all three coins, so the filter selects for
late entries, not good ones.

**Next experiment (only if revisited):** drop the regime filter, trade
the raw signal cross with a 1.5xATR stop and 48-bar max hold. That
tests whether the double-smoothed cross has any timing value at all
before the filter buries it. Expectation: still negative — the lag is
structural.

**Do not:** lengthen R/S — more smoothing is the opposite of what this
needs.
