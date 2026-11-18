# Quasimodo Reversal — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Pivot width | 5 bars (centre ± 2) | The spec's "same causal 5-bar pivots as the other pattern strategies". |
| Break trigger | close beyond the neckline (L1 / H1) | The spec's "a close below L1 printing a lower low". |
| Shoulder trigger | close beyond the shoulder swing level (RL / RH) | The spec's entry rule, "sell at the bearish shoulder, or on a close below the shoulder's local low". |
| Break expiry / retrace expiry / shoulder expiry | 50 / 30 / 20 bars | Stale-structure guards (see decision 3); not in the sources, set a priori so a pattern cannot linger indefinitely. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Pivots need 5 bars to confirm and a full QM sequence needs ~25 bars to form; 60 gives margin. |

## Spec decisions / ambiguities

1. **The shoulder must be a genuine retracement leg.** The spec
   says only "record the swing low RL formed during the
   retracement leg". Shipped reading adds two guards, both
   documented here: (a) RL must sit above the lowest low printed
   since the break bar — otherwise the "shoulder" is just the
   breakdown low itself, and the entry would fire on ordinary
   continuation; (b) the retracement must actually get back across
   the broken neckline (bearish: max high since the break above
   L1; bullish: min low since the break below H1) before a swing
   low/high can arm the shoulder. Without (b), a shallow bounce
   that never retests the neckline would count as a Quasimodo.
2. **Head invalidation is asymmetric by stage.** While waiting for
   the break, a *close* beyond the head invalidates (a wick above
   the head that closes back inside does not). During the
   retracement, *any* high above the head (bearish) / low below
   the head (bullish) invalidates, because the retracement has by
   definition exceeded the head. Both are interpretation choices.
3. **Expiries are invented, not sourced.** The sources give no
   time limits; 50 bars to break after the head, 30 bars to form
   the shoulder after the break, and 20 bars to trigger after the
   shoulder arms are a priori staleness guards. A pattern that
   expires restarts from the next confirmed swing.
4. **A higher head replaces the old one.** While waiting for the
   break, a newly confirmed swing high above H2 (bearish) becomes
   the new head; while waiting for the head, a lower swing low
   updates L1 (bearish) / a higher swing high updates H1
   (bullish). The sequence is tracked by swing order, not by
   fixed levels.
5. **`qm_state` collapses the two sides.** The column reports the
   furthest-along stage over both machines (0 none, 1 head formed,
   2 break confirmed, 3 shoulder armed); `qm_side` (+1 bearish /
   -1 bullish / 0 none) says which side is furthest along. The
   trigger columns and the per-side head levels carry the rest.
6. **Exits use the most recent head level.** The invalidation level
   is the last formed head (`last_bear_head_high` /
   `last_bull_head_low`, forward-filled). If a newer head forms
   while a trade is open, the level updates to the newer head.
7. **Harness stop/trail as an additional exit.** The spec's exits
   are the opposite-QM signal / head invalidation; the
   batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar
   max hold) is applied on top, per the batch instruction.

## What the exits actually did

Shipped run (22 trades): all 22 trades ended on the harness
stop/trail and none on a signal exit. The opposite-QM signal and
the head-invalidation close never fired before the 2xATR stop on
any trade — the QM entry is rare, and once entered the position
is carried by the stop/trail alone.

No bug fixes requiring re-runs, no PnL-selected tuning.
