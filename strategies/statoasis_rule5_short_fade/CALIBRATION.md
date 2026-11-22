# StatOasis Rule 5 — Calibration

All parameters were fixed **a priori** from the published Rule 5
specification — there is no in-sample sweep, so there is nothing
to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| RSI threshold | > 70 short / < 30 long | the rule's own overbought/oversold levels; 30 is the symmetric mirror for the builder-added long |
| Williams %R | > −10 short / < −90 long | the rule's own "double-overbought" confirmation: close within 10% of the 14-bar range top; −90 is the symmetric mirror |
| Williams %R length | 14 | the rule's own length, matching RSI(14) |
| SMA trend | 100 bars, falling/rising by 1-bar change | the rule's own trend filter; a 1-bar change is the most literal reading of "SMA(100) is falling" |
| Hold | 5 bars fixed | the rule's own exit; adapted 1:1 in bars (5h on 1h data, vs 5 days on the original daily SPY test) |
| Stop | 2×ATR(14) | roomy backstop so the fixed hold, not the stop, normally ends the trade; the original rule carries no stop of its own |
| Trail / target | none | the fixed hold is the entire trade management |
| Max hold | 5 bars | mirrors the signal-level hold as a harness backstop |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 120 bars | SMA(100) + margin |

## Deviations from the source, stated plainly

1. **Daily SPY → 1h crypto.** The 5-bar hold is 5 hours here,
   not 5 days; the momentum conditions fire far more often on 1h
   bars, and crypto's 24/7 trend persistence differs from SPY
   daily. The in-sample/out-of-sample split that made Rule 5
   interesting on SPY does not transfer — this window is one
   continuous in-sample run.
2. **Long mirror is builder-added.** Rule 5 as published is
   short-only; the RSI < 30 / %R < −90 / SMA(100) rising long is
   our symmetric extension.
3. **No stop in the original.** The 2×ATR stop is a harness
   backstop, not part of Rule 5.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers — least of all the RSI /
%R thresholds, which are exactly the kind of knobs that
overfit a fade rule.
