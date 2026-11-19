# Fibonacci Time Zones Pullback — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Pivot window | 10 bars [j-7, j+2], confirmed at centre+2 | Shared pivot convention with schiff_pitchfork (see its CALIBRATION.md decision 1); the spec says "confirmed 10-bar swing high/low". |
| Zone counts / tolerance | 8, 13, 21, 34 / ±1 bar | The spec's Fib counts and tolerance, verbatim. |
| Trend filter | close > EMA(50) for longs, < EMA(50) for shorts | The spec's uptrend/downtrend condition, verbatim. |
| Pullback | close below/above EMA(20) since the anchor, then a cross back | The spec's pullback-reversal, verbatim; the cross-back bar must fall inside the zone window. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | EMA(50) needs 50 bars; 60 gives margin. |

## Spec decisions / ambiguities

1. **The zone gates the reclaim, not the dip.** The spec's
   pullback is "a close below EMA(20) and then a close back
   above EMA(20) inside the zone window". Shipped reading: the
   dip may occur at any point since the anchor bar (including at
   the anchor itself — a swing low is usually already below
   EMA(20)), but the reclaim cross must land inside the ±1-bar
   zone window. A reclaim that lands before the window, or after
   it passes, is no trade.
2. **The reclaim must be a genuine cross.** The reclaim bar's
   close must be above EMA(20) while the previous bar's close
   was at or below its EMA(20). A bar that merely stays above
   EMA(20) inside a zone window does not trigger — there must
   have been a pullback to reclaim from.
3. **The dip flag is seeded from the anchor bar.** When a swing
   low confirms, the flag is set from the closes between the
   anchor centre bar and the confirmation bar, so a dip that
   printed at the swing low itself counts. Otherwise the first
   two bars of every anchor would be blind.
4. **A new swing of either kind re-anchors.** The spec says "a
   new confirmed swing re-anchors the zones" without restricting
   kind, so a swing high re-anchors a swing-low anchor (and
   flips the tradeable side) and vice versa.
5. **Exit levels are the most recent confirmed swings.** The
   "anchor low/high" in the exit rule is the most recent
   confirmed swing low/high, forward-filled — if a newer swing
   forms while a trade is open, the exit level updates to it.
6. **If one bar confirms both a swing high and a swing low** (a
   single bar that is both extremes of its 10-bar window), the
   high wins the anchor. This is vanishingly rare and is a
   tie-break, not a rule from the source.

## What the exits actually did

Shipped run (128 trades): 110 trades ended on the harness
stop/trail and 18 on a signal exit (opposite signal or close
through the anchor extreme). The stop does most of the work;
the anchor-extreme exit rarely fires first.

No bug fixes requiring re-runs, no PnL-selected tuning.
