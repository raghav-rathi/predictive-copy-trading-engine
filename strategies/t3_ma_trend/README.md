# Tillson T3 Trend

The T3 (Tim Tillson, 1998) is a lag-reduced moving average built
from a stack of six EMAs of the same period, combined with
weights that sum to one:

```
e1..e6 = six successive EMAs of C, period n
c1 = -v^3,  c2 = 3v^2 + 3v^3,  c3 = -6v^2 - 3v - 3v^3,
c4 = 1 + 3v + v^3 + 3v^2
T3 = c1*e6 + c2*e5 + c3*e4 + c4*e3
```

With vfactor 0.7 the weights are c1 = -0.343, c2 = 2.499,
c3 = -6.069, c4 = 4.913. The negative weights on the deeper EMAs
subtract out the lag the stack accumulates, so T3 tracks price
far more closely than a single EMA of the same period while
smoothing more than a raw EMA. T3 is a lag-reduced EMA stack,
not a new indicator family — it is a better EMA, and it should
be judged as one.

## Rule (long)

```
close > T3(10, 0.7) AND T3(10) rising AND T3(10) > T3(30, 0.7)
```

- **Exit long:** close back through T3(10) (C < T3) OR T3(10)
  turns down.
- **Short mirror:** close < T3(10) AND T3(10) falling AND
  T3(10) < T3(30, 0.7); exit on a close above T3(10) or T3(10)
  turning up.
- **Entries are transitions only:** a state machine tracks the
  open position, so a setup that stays true for twenty bars
  enters once. An opposite setup on the same bar as an exit
  flips the position.

## 1h scaling (documented)

- T3(10) ≈ a 10-hour trigger; T3(30) ≈ a 30-hour (1.25-day)
  slow confirmation. The fast/slow pair is Tillson's own
  vfactor-0.7 default carried to hourly bars unchanged.
- Each EMA is seeded at the first close (pandas ewm,
  min_periods=1), exactly as in the standard Tillson
  implementation — T3 is defined from bar 0 with no lookahead
  and no NaN. Early bars carry a warm-up bias, which is why
  WARMUP is 60 bars.

## Honest flags

- **T3 overshoots after sharp steps.** The negative weights ring
  past a sudden move: after a step from 100 to 120 held for 40
  bars, T3(10) settles slightly *above* 120 (unit-tested). On
  gap-prone crypto that overshoot can put the average on the
  wrong side of price right after a jump. See CALIBRATION.md.
- **Same whipsaw failure as the Hull average.** T3(10) turns
  almost as fast as price, so on choppy 1h crypto the strategy
  averaged a 5.9-bar hold and 465 trades on BTC — a loser on
  all three coins (see BACKTEST.md). The slower T3(30)
  confirmation gate did not save it: it agrees with the fast
  T3 most of the time, so it filters little.
- **No parameter tuning was done.** n = 10/30 and vfactor 0.7
  are Tillson's defaults, fixed a priori.

## Risk

2×ATR(14) harness stop as a backstop (the signal-level T3 exit
is the real stop), no trail, no target, 168-bar (~7-day) max
hold, 1% risk per trade, 3× leverage cap. WARMUP = 60 bars
(six stacked EMAs of period 30 need ~2–3 periods to settle).

Source: Tim Tillson, "Smoothing Techniques for More Accurate
Signals", *Technical Analysis of Stocks & Commodities*,
January 1998 (https://www.mesasoftware.com/papers/T3.pdf).
