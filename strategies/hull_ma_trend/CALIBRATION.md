# Hull MA Trend — Calibration

All parameters were fixed **a priori** from Hull's published
specification and 1h-bar reasoning — there is no in-sample sweep,
so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| HMA fast | 16 bars | Hull's canonical fast length; the trigger — ~16h on 1h bars |
| HMA slow | 64 bars | Hull's canonical slow length; the trend filter — ~2.7 days on 1h bars |
| Long entry | C > HMA(16), HMA(16) rising, C > HMA(64) | price above the fast average, the fast average itself rising, and price above the slow average — trigger + momentum + regime, all three required |
| Exit | close below HMA(16) or HMA(16) turning down | the fast average is the trailing mechanism; a turn against the position ends the trade |
| Harness stop | 2×ATR(14) | backstop only — the signal-level HMA exit is the real stop |
| Trail / target | none | the HMA itself trails; a target would cut the trend rides the method is built for |
| Max hold | 168 bars (~7 days) | caps a ride that has gone flat; never fired in the backtest (average hold 3.5 bars) |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 100 bars | HMA(64) first valid at bar 71, plus margin |

## Deviations from the source, stated plainly

1. **Short mirror is builder-added.** Hull's HMA is directionless
   — it is an average, not a long-only system — so the symmetric
   short is a natural extension, but it is ours, not Hull's.
2. **1h scaling.** Hull's lengths are used unchanged on hourly
   bars (16/64 bars ≈ 16h/2.7d). No re-scaling was applied.
3. **Seeding.** Before the first valid value each HMA column is
   seeded with the bar's own close (causal, documented in
   `indicators.py`). The seed is signal-neutral: `C > HMA` is
   False when HMA == C.

## Spec corrections surfaced while implementing

- **HMA on a linear series is not exactly the close.** The
  textbook claim that HMA "tracks a straight line with no lag"
  holds exactly only when sqrt(n) == 2 (n = 4). For n = 16 the
  algebra leaves a lag of exactly 2/3 of a bar-step on a
  unit-slope ramp (verified numerically and unit-tested). The
  lag-halving claim still holds — HMA(16) beats EMA(16) on a
  step — but "zero lag" is an oversimplification. No parameter
  was changed on the strength of this; it is recorded here.
- **No alternates tried.** The 16/64 pair was shipped as
  specified. The whipsaw outcome (see BACKTEST.md) was not
  chased with alternate lengths.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers — least of all the
16/64 lengths, which directly control how many trades fire.
