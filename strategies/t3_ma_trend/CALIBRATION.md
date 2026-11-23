# Tillson T3 Trend — Calibration

All parameters were fixed **a priori** from Tillson's published
specification and 1h-bar reasoning — there is no in-sample sweep,
so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| T3 fast | n=10, vfactor=0.7 | Tillson's default period and vfactor; the trigger — ~10h on 1h bars |
| T3 slow | n=30, vfactor=0.7 | same vfactor, 3x the period; the confirmation gate — ~30h on 1h bars |
| Long entry | C > T3(10), T3(10) rising, T3(10) > T3(30) | price above the fast T3, the fast T3 itself rising, and the fast T3 above the slow T3 — trigger + momentum + agreement |
| Exit | close back through T3(10) or T3(10) turning down | the fast T3 is the trailing mechanism; a turn against the position ends the trade |
| Harness stop | 2×ATR(14) | backstop only — the signal-level T3 exit is the real stop |
| Trail / target | none | the T3 itself trails; a target would cut the trend rides the method is built for |
| Max hold | 168 bars (~7 days) | caps a ride that has gone flat; never fired in the backtest (average hold 5.9 bars) |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 60 bars | six stacked EMAs of period 30 need ~2–3 periods to settle |

## Deviations from the source, stated plainly

1. **Short mirror is builder-added.** Tillson's paper is about
   the smoother, not a trading system; the symmetric short is
   ours.
2. **1h scaling.** Tillson's defaults (n=10, vfactor=0.7) are used
   unchanged on hourly bars. No re-scaling was applied.
3. **EMA seeding.** Each EMA is seeded at the first close
   (pandas ewm, min_periods=1, adjust=False), as in the standard
   Tillson implementation. The alternative — chaining
   min_periods=n EMAs — would leave T3 undefined for the first
   59 bars and is not what Tillson implementations do; the
   seeding choice is documented in `indicators.py`.

## Spec corrections surfaced while implementing

- **T3 overshoots after sharp steps.** The negative weights
  (c1 = -0.343, c3 = -6.069) ring past a sudden move: after a
  step from 100 to 120 held for 40 bars, T3(10) settles at
  ~120.12, slightly *above* the new level (verified numerically
  and unit-tested). The paper presents T3 as a smoother; it does
  not warn that the smoother can sit on the wrong side of price
  after a jump. On gap-prone crypto this is a live failure mode
  for any exit that keys off "close through T3". No parameter was
  changed on the strength of this; it is recorded here.
- **vfactor 0 collapses T3 to a triple EMA.** With v = 0 the
  weights become c1 = c2 = c3 = 0, c4 = 1, so T3 == e3. This is
  a useful sanity check on the implementation (unit-tested) and
  confirms T3 is a weighted EMA stack, not a new indicator
  family.
- **No alternates tried.** The 10/30 pair at vfactor 0.7 was
  shipped as specified. The whipsaw outcome (see BACKTEST.md)
  was not chased with alternate periods or vfactors.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers — least of all the
10/30 periods or the 0.7 vfactor, which directly control how many
trades fire.
