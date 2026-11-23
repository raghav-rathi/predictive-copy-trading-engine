# Wilder Parabolic SAR — Calibration

All parameters were fixed **a priori** from Wilder (1978) and
1h-bar reasoning — there is no in-sample sweep, so there is
nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| AF step | 0.02 | Wilder's own step — the SAR accelerates by 0.02 per new extreme |
| AF max | 0.20 | Wilder's own cap — the SAR never accelerates faster than this |
| Seed | LONG, SAR = low[0], EP = high[0] | no prior trend exists on bar 0; the seed is arbitrary, so the signal layer emits no entry on bar 0 and the first trade is the first genuine flip |
| SAR clamp | prior two bars' low/high | Wilder's rule: in an uptrend the SAR may never exceed the lowest low of the prior two bars (mirror in a downtrend) |
| Flip | low < SAR (long) / high > SAR (short) | the trend reverses the moment price penetrates the SAR |
| Harness stop | 2×ATR(14) | backstop only — the SAR flip is the real exit |
| Trail / target | none | the SAR itself is the trailing stop; adding a second trail would fight it |
| Max hold | 336 bars (~14 days) | caps a stale trend that never flips |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 20 bars | PSAR seeds from bar 0; 20 bars of margin |

## Deviations from the source, stated plainly

1. **No flat state in the original.** Wilder's system is
   always in the market. We add a flat state only before the
   first flip (bar 0 emits no entry), because the seed is
   arbitrary and must not manufacture a trade. After the first
   flip the system is always in, exactly as Wilder wrote it.
2. **Next-bar-open execution.** The flip is confirmed on bar
   i's close and executed at bar i+1's open, per the house
   convention — Wilder's original assumes execution at the
   flip price. This costs a bar of slippage on every flip and
   is part of why the backtest is so negative.
3. **1h scaling.** Wilder designed PSAR on daily bars. On 1h
   bars the SAR flips far more often (a flip every ~12 bars
   in this window), which is the whipsaw mechanism behind the
   loss — see BACKTEST.md.

## Spec corrections surfaced while implementing

- The task's "first bar if seeded long" phrasing was
  ambiguous; resolved as: **no entry on bar 0, ever**. The
  first entry is the first flip after bar 0. This is the only
  reading consistent with "do NOT emit an entry on bar 0 from
  seeding alone."
- The clamp uses the prior two bars' extremes, not the
  current bar's — the current bar's low is the flip test
  itself, so it cannot also be the clamp.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — least of all
the AF step/max, which directly control flip frequency.
