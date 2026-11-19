# Mitigation Block — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Pivot width | 5 bars (centre ± 2) | The spec's "causal 5-bar pivots, as in quasimodo". |
| Failure swing | H2 strictly below H1 (bearish) / L2 strictly above L1 (bullish) | The spec's "LOWER high" / "HIGHER low": a rally that reaches the prior high exactly is not a failure swing, it is a test of it. |
| Traded-through test | any HIGH above H1 (bearish) / any LOW below L1 (bullish) while the failure swing is forming invalidates the setup | The spec's "the prior high is NEVER traded through" — a wick through counts, not just a close. |
| Break trigger | close below L1 / above H1 | The spec's "closes below L1 (structure break)". |
| Block candle | the bar at the L1 / H1 centre (the pivot-confirmation bar's candle) | The spec's parenthetical definition. The "last up-close / down-close" wording is satisfied in the canonical case; the centre bar is the operative definition used here (see decision 2). |
| Entry | first close inside the block range after the break | The spec's "first return into the block (close inside the block range)". |
| Block expiry | 150 bars after the break | The spec's expiry. |
| Block replacement | a newer break on the same side replaces an armed block | The spec's "only the most recent block per side is active". |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Pivots need 5 bars and a full failure-swing sequence needs ~17 bars; 60 gives margin. |

## Spec decisions / ambiguities

1. **No stage expiries before the break.** The spec gives an
   expiry only for armed blocks (150 bars). A setup sitting in
   stage 1–3 does not expire; it waits for the next pivot or
   invalidation. A stale H1/L1 can therefore arm a block long
   after it formed — a documented consequence of the spec.
2. **The block candle is the centre bar, unconditionally.** The
   spec calls it "the last up-close candle at L1" and then
   defines it as the pivot-confirmation bar's candle (the bar at
   the L1 centre). Shipped reading uses the centre bar's [low,
   high] whether or not that bar closed up (bearish) / down
   (bullish); hunting for a different up-close bar near L1 would
   be a second interpretation with no anchor in the spec.
3. **A close through the block clears it.** Before entry, a close
   above a bearish block's high means price blew through the
   supply zone without returning into it, so the block is dead;
   after entry the same close is the exit. The zone is published
   for the clearing bar itself so the signal layer sees the exit.
4. **A deeper pullback updates L1 / a higher bounce updates H1.**
   While the failure swing is forming, a new swing low below L1
   (bearish) becomes the new L1 (and the new block candle); a new
   swing high between H2 and H1 becomes the new H2. The sequence
   is tracked by swing order, not fixed levels.
5. **The setup machine keeps running while a block is armed.**
   The setup and the armed block are independent states: a fresh
   failure-swing sequence can complete while an older block is
   still armed, and its break replaces the older block.
6. **`mb_state` collapses the two sides.** 0 none, 1 a setup is
   forming, 2 a block is armed (max over the two sides);
   `mb_side` (+1 bearish / -1 bullish / 0) says which side is
   furthest along. The trigger columns and the per-side block
   levels carry the rest.

## What the exits actually did

Shipped run (411 trades): 255 trades ended on the harness stop /
trail and 156 on a signal exit (close through the block or
opposite signal). The 2xATR stop is the working exit more often
than the block exit — once entered, the position is usually
carried by the stop/trail, and the block level rarely gets
retested as an exit before the stop fires.

No bug fixes requiring re-runs, no PnL-selected tuning.
