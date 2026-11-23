# Fisher Transform Trend — Calibration

All parameters were fixed **a priori** from the Ehlers Fisher
Transform specification and 1h-bar reasoning — there is no
in-sample sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Normalization window | 10 bars | Ehlers' own window for the Fisher Transform |
| x clamp | ±0.999 | keeps (1+x)/(1−x) finite and positive; the log explodes at ±1 |
| Fisher smoothing | 0.5 / 0.5 recursion | the spec's smoothing: fisher[i] = 0.5·fisher_raw[i] + 0.5·fisher[i−1] |
| Entry trigger | 0-cross + rising/falling | the spec's trigger; the cross is the regime flip |
| Exit | cross back through 0, or two bars turning against | cross-back is the symmetric trigger; the two-bar turn is the spec's trend-failure exit |
| Flip on cross-back | yes | the cross is simultaneously an exit and a fresh opposite entry |
| Max hold | 120 bars (~5 days) | caps a stale Fisher ride; a 0-cross trend that has not run in five days is noise |
| Harness stop | 2×ATR(14) | backstop only — the signal-level exits are the real exits |
| Trail / target | none | the method exits on the cross or the turn, not on a trail or target |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 30 bars | 10-bar window + smoothing settle + margin |

## Deviations and spec corrections, stated plainly

1. **No intermediate value-smoothing step.** Ehlers' full
   published Fisher procedure smooths the normalized value
   itself first (value[i] = 0.66·(2·raw−1) + 0.34·value[i−1])
   before the transform. The assigned spec for this strategy
   transforms the raw normalized value directly and smooths
   only the Fisher output. This strategy follows the assigned
   spec exactly; the value-smoothed variant already exists in
   this repo as `fisher_transform`, so the two are genuinely
   different implementations and are not duplicates.
2. **Bar-0 cross is undefined.** A cross needs a previous bar,
   so signals.py emits nothing on bar 0 (it seeds prev from a
   notional 0.0 only from bar 1 onward). The shipped Fisher
   series starts at 0.0 anyway, so this affects synthetic
   inputs only.
3. **1h scaling.** The 10-bar window is 10 hours on 1h bars
   versus 10 days in the daily original. The transform
   whipsaws far more often at this resolution — that is the
   documented cost of the port, and the backtest shows it
   plainly (see BACKTEST.md).
4. **Short mirror is builder-added.** Ehlers presents the
   Fisher Transform primarily as a reversal/timing tool; the
   symmetric short system is our extension.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — least of all
the 10-bar window or the 0-cross rule, which directly control
how many trades fire.
