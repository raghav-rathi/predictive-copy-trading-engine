# Livermore Pivotal Point — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Consolidation window / narrow threshold | 20 bars / range < 0.6x median of prior 100 20-bar ranges | The spec's consolidation definition, verbatim. |
| Break volume | > 1.25x the 20-bar mean volume | The spec's "expanding volume". |
| Reaction window / contraction | 10 bars / volume below the 20-bar mean, low holding the pivot | The spec's "within the next 10 bars ... volume below the 20-bar mean". |
| Resumption volume | volume above the 20-bar mean | The spec's "volume above the 20-bar mean". |
| Resumption expiry | 20 bars after the reaction | Staleness guard, not in the sources; set a priori so an armed reaction cannot linger indefinitely. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 120 | The range median needs 100 prior 20-bar windows; 120 gives margin. |

## Spec decisions / ambiguities

1. **The reaction bar needs a pullback close.** The spec says
   price "pulls back" — shipped reading requires the reaction
   bar's close to be below the break bar's close, so a bar that
   merely prints a lower low while closing higher does not count
   as a reaction. A bar that closes above the break close is
   continuation, not a reaction.
2. **The reaction high is the highest high from the break bar
   through the reaction bar.** The spec says "a close above the
   reaction high" without defining it; shipped reading uses the
   break-to-reaction range high, which is the level the resumption
   must clear.
3. **A new consolidation resets an in-progress setup.** The spec
   says a new consolidation "replaces the active pivot"; shipped
   reading also resets the break/reaction stage, because the old
   break was measured against a pivot that no longer exists.
4. **A close back through the pivot invalidates before
   resumption.** The spec's danger signal is the exit rule;
   shipped reading applies it inside the setup too — a setup
   whose price falls back below the bull pivot (long) before the
   resumption is dead, not merely untriggered.
5. **The 20-bar resumption expiry is invented, not sourced.**
   Livermore gives no time limit; 20 bars after the reaction is
   an a priori staleness guard. A setup that expires restarts
   from the next consolidation.
6. **Volume means include the current bar.** The 20-bar mean
   volume on bar i includes bar i's own volume, so a break bar
   must clear 1.25x a mean that already contains its own spike.
   This is the conservative reading.

## What the exits actually did

Shipped run (116 trades): 102 trades ended on the harness
stop/trail and 14 on a signal exit (pivot violation or opposite
signal). The danger-signal exit fires sometimes, but the stop
does most of the work.

No bug fixes requiring re-runs, no PnL-selected tuning.
