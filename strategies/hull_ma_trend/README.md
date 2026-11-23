# Hull Moving Average Trend

The Hull Moving Average (Alan Hull, 2005) is a weighted moving
average designed to do two things at once: react fast and stay
smooth. It does it with one algebraic trick —

```
HMA(n) = WMA(2*WMA(C, n/2) - WMA(C, n), sqrt(n))
```

The `2*WMA(n/2) - WMA(n)` term over-weights recent price (a
weighted average of the short half, doubled, minus the long
average), and the final `WMA(sqrt(n))` smooths the overshoot
back out. The result halves the lag of an EMA of the same length:
on a step up, HMA(16) sits measurably closer to the new level
than EMA(16) (unit-tested). HMA's speed is the point — it is a
trend filter that turns almost as fast as price itself.

## Rule (long)

```
close > HMA(16) AND HMA(16) rising AND close > HMA(64)
```

- **Exit long:** close below HMA(16) OR HMA(16) turns down.
- **Short mirror:** close < HMA(16) AND HMA(16) falling AND
  close < HMA(64); exit on a close above HMA(16) or HMA(16)
  turning up.
- **Entries are transitions only:** a state machine tracks the
  open position, so a setup that stays true for twenty bars
  enters once. An opposite setup on the same bar as an exit
  flips the position.

## 1h scaling (documented)

- HMA(16) ≈ a 16-hour trigger; HMA(64) ≈ a 2.7-day trend filter.
- The fast average is the trigger and the slow average is the
  regime gate — the same 16/64 split Hull's readers use on daily
  bars, carried to hourly bars unchanged. No re-scaling was
  applied: the point of the test is whether Hull's own lengths
  survive on 1h crypto.
- WMA is implemented in `indicators.py` (base.py has no WMA).
  Before the first valid value each HMA column is seeded with
  the bar's own close (causal, never NaN); the seed is neutral
  for signals because `C > HMA` is False when HMA == C.

## Honest flags

- **HMA's speed cuts both ways.** The same fast turn that halves
  lag also flips the signal on every hourly wiggle. On this
  window the strategy averaged a 3.5-bar hold and 883 trades on
  BTC alone — it is a whipsaw machine on choppy 1h crypto, and
  the backtest shows it: a loser on all three coins (see
  BACKTEST.md).
- **No parameter tuning was done.** The 16/64 lengths are Hull's
  canonical pair, fixed a priori. Loosening the exit (e.g. only
  exiting on the slow-average cross) would cut the trade count,
  but that would be tuning on this window, so it is not done
  here.

## Risk

2×ATR(14) harness stop as a backstop (the signal-level HMA exit
is the real stop), no trail, no target, 168-bar (~7-day) max
hold, 1% risk per trade, 3× leverage cap. WARMUP = 100 bars
(HMA(64) is first valid at bar 71, plus margin).

Source: Alan Hull, "Hull Moving Average" (2005)
(https://alanhull.com/hull-moving-average).
