# Instantaneous Trendline — Calibration

All parameters were fixed **a priori** from the Ehlers
Instantaneous Trendline specification and 1h-bar reasoning —
there is no in-sample sweep, so there is nothing to select on
this window.

| Parameter | Value | Rationale |
|---|---|---|
| Alpha | 0.07 | Ehlers' book constant (the 7-day-equivalent smoothing for daily bars), ported **unscaled** to 1h — a documented choice, not a tuned one |
| Entry | C > IT and IT rising (mirror for shorts) | the spec's trend definition: price on the trend side of the line, line moving with it |
| Transition-only entries | yes | a position opens only when the condition first becomes true; no re-entry while it persists |
| Exit | C back through IT, or IT turning against | the spec's exits: the trend is over when price re-crosses the line or the line reverses |
| Flip on opposite transition | yes | an opposite transition is simultaneously an exit and a fresh entry |
| Max hold | 168 bars (~7 days) | caps a stale trendline ride |
| Harness stop | 2×ATR(14) | backstop only — the signal-level exits are the real exits |
| Trail / target | none | the method exits on the cross-back or the turn, not on a trail or target |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 30 bars | filter settles in a handful of bars; 30 is ample margin |

## Deviations and spec corrections, stated plainly

1. **Alpha ported unscaled.** Alpha = 0.07 is Ehlers'
   daily-bar constant. On 1h bars the same alpha makes the
   filter much faster relative to the bar — it hugs price and
   whipsaws. That is the documented cost of the port, and the
   backtest shows it plainly (see BACKTEST.md). Slowing alpha
   for hourly bars would be a new strategy, not a correction,
   and is not adopted here.
2. **Seeding differs from the sibling strategy.** This spec
   seeds IT[0] = C[0], IT[1] = C[1]. The existing
   `ehlers_instantaneous_trendline` strategy seeds IT[1] as
   the mean of the first two closes. The two specs differ
   here; this one follows the assigned spec exactly, and the
   seed is irrelevant after the 30-bar warmup either way.
3. **Bar-0 conditions are false.** At bar 0 there is no prior
   trendline value, so rising/falling are undefined and both
   entry conditions are false. The shipped filter starts at
   the close anyway, so this affects synthetic inputs only.
4. **Short mirror is builder-added.** Ehlers presents the
   Instantaneous Trendline primarily as a trend filter for
   long-side timing; the symmetric short system is our
   extension.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — least of all
alpha, which directly controls how many trades fire.
