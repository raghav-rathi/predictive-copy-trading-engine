# Wilder ADX/DMI Trend System — Calibration

All parameters were fixed **a priori** from Wilder's published
specification and 1h-bar reasoning — there is no in-sample
sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| ADX / DI length | 14 bars | Wilder's own length for ADX, +DI, -DI |
| Trend gate | ADX > 25 | Wilder's own trend-strength rule — trade only when a trend is present |
| Exit threshold | ADX < 20 | Wilder's own exit: the trend has failed when ADX falls below 20; the 25/20 pair is hysteresis, so a wobble between them does not churn the position |
| Entry | DI cross, transition only | +DI crossing above -DI (long); staying crossed is not a new entry |
| Exit | opposite DI cross OR ADX < 20 | the cross is the trend-reversal exit; the ADX floor is the trend-failure exit |
| Flip | opposite setup while holding exits + enters | follows from the exit rule (an opposite cross is by construction the long exit condition); made explicit in signals.py |
| Max hold | 168 bars (~7 days) | a Wilder trend that has not run in a week on 1h bars was not a trend; never bound in the backtest (0 max-hold exits) |
| Harness stop | 2xATR(14) | backstop only — the signal-level cross/ADX exit is the real stop |
| Trail / target | none | Wilder's system exits on the cross / trend failure, not on a trail or target |
| Risk | 1% / trade, 3x leverage cap | house standard |
| Warmup | 40 bars | ADX(14) needs ~14 bars to seed the DIs plus smoothing time for DX/ADX; 40 covers it |

## Spec corrections surfaced while implementing

1. **A single sustained ramp cannot fire a setup — and that is
   the spec working, not a bug.** The DI cross happens on the
   first trending bar, before ADX has built above 25 (ADX needs
   several bars of DX = 100 to rise past 25), and the cross and
   the gate must coincide on the same bar. So a trend that
   starts from flat never triggers its own first cross; the
   system only enters on a *later* cross, once ADX is already
   high — i.e. on a pullback-and-resume or a reversal inside an
   established trend. This is inherent to Wilder's rules as
   specified (cross + gate on the same bar) and is covered by a
   dedicated unit test (`test_both_setups_fire_on_zigzag`):
   a zigzag (up, down, up) fires both sides, while a single
   ramp fires neither. We did not loosen the gate or lag the
   cross to force trades.
2. **No other corrections.** `base.adx` returns exactly the
   specified triple (ADX, +DI, −DI) with Wilder smoothing, and
   its seeding (NaN until the DIs are valid) matches the
   documented seeding in indicators.py.

## Deviations from the source, stated plainly

1. **1h scaling.** ADX(14) is used as published with no
   rescaling; on 1h bars the 14-bar smoothing is a ~14-hour
   memory, so the system reacts to intraday trend structure
   rather than the multi-week trends Wilder traded daily.
2. **Next-bar-open execution.** The cross is entered at the
   next bar's open, not at the cross close.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — least of all
the 25/20 ADX thresholds, which directly control how many
trades fire.
