# Donchian Turtle Breakout (System 1) — Calibration

All parameters were fixed **a priori** from the published
Turtle specification and 1h-bar reasoning — there is no
in-sample sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Entry channel | 20 bars | System 1's own 20-day entry, scaled to 20 bars on 1h |
| Exit channel | 10 bars | System 1's own 10-day exit, scaled to 10 bars on 1h |
| Channel basis | prior bars only (shift 1) | the breakout level must be known before the bar opens; a bar cannot break out on its own high/low |
| Stop | 2×ATR(20) | the Turtles' own volatility stop (N = ATR(20)) |
| Trail / target | none | the system exits on the 10-bar channel or the stop, not on a trail or target |
| Max hold | 336 bars (~14 days) | caps a position that never triggers either exit; in practice the 10-bar exit fires first (no max-hold exits in the backtest) |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 60 bars | 20-bar channel + 20-bar ATR, with margin |

## Deviations from the source, stated plainly

1. **System 1 only.** No 55-day System 2 entry/exit.
2. **Skip rule omitted.** The Turtles skipped a breakout if
   the previous breakout in that market was a winner. This
   implementation takes every breakout. The omission was in
   the build spec and is documented in the README; it raises
   the trade count versus the original and trades breakouts
   into already-extended moves.
3. **No pyramiding.** The original added to winners (up to 4
   units). One position at a time here — the harness enforces
   it and the signal layer never re-enters while holding.
4. **1h scaling.** 20 days become 20 hours. The daily
   original's trend filter becomes an intraday breakout on 1h,
   which whipsaws far more (510 trades, 29.6% win rate — see
   BACKTEST.md).
5. **Flip on simultaneous exit + opposite breakout.** If a
   close breaks the 10-bar exit level and the 20-bar entry
   level in the opposite direction on the same bar, the
   position flips. The original would exit and then take the
   new breakout as a fresh signal; the net effect is the same
   trade, one bar earlier in execution terms.

## Spec corrections surfaced while implementing

- None to the core rules. One clarification: the exit channel
  is also prior-bars-only (shifted by 1), matching the entry
  channel — a close below the prior-10-bar low, not below a
  low that includes the current bar's own low (which would
  make the exit trigger on almost any down bar).

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — least of all
the 20/10 channel lengths, which directly control how many
trades fire.
