# Keltner Channel + MACD Combo — Calibration

All parameters were fixed **a priori** from the published
Raschke/Appel specification and 1h-bar reasoning — there is no
in-sample sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Keltner mid | EMA(20) of close | Raschke's channel midline as published |
| Keltner ATR | ATR(10) | the channel's own ATR length |
| Keltner multiplier | 1.5x ATR | the published channel width |
| MACD | (12, 26, 9) | Appel's standard MACD |
| Momentum agreement | histogram > 0 long / < 0 short, same bar | the dual-agreement filter: momentum must agree with the break on the bar it happens |
| Breakout definition | transition only (prior close at/below the band) | staying above the band is not a new breakout |
| Exit | close back inside the channel OR histogram flipping sign | the channel re-entry is the failed-breakout exit; the histogram flip is the momentum exit |
| Flip | opposite setup while holding exits + enters | follows from the exit rule (a short breakout bar is a close back inside the channel for a long); made explicit in signals.py |
| Max hold | 120 bars (~5 days) | a breakout that has not run in five days was not a breakout; never bound in the backtest (0 max-hold exits) |
| Harness stop | 2xATR(14) | backstop only — the signal-level channel exit is the real stop |
| Trail / target | none | the method exits on channel re-entry / histogram flip, not on a trail or target |
| Risk | 1% / trade, 3x leverage cap | house standard |
| Warmup | 40 bars | MACD signal/histogram needs ~34 bars to seed; 40 covers the Keltner EMA(20) as well |

## Spec corrections surfaced while implementing

None material. One judgment call, documented in signals.py and
above: the brief does not state whether an opposite setup while
holding flips the position or merely exits it. We flip, because
the opposite breakout bar necessarily satisfies the exit
condition for the held side (a close below the lower band is
also a close below the upper band), so flip vs exit-only differ
only in whether the new side is entered on the same bar.

## Deviations from the source, stated plainly

1. **1h scaling.** Keltner/MACD lengths are used as published
   with no rescaling; on 1h bars the 20-bar EMA is a ~20-hour
   midline, so the channel is much tighter relative to daily
   structure than in Raschke's daily original.
2. **Next-bar-open execution.** The breakout is entered at the
   next bar's open, not at the breakout close — a one-bar lag
   the book version does not have.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — least of all
the exit rule, which directly controls how many trades fire.
