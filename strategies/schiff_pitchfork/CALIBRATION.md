# Schiff Pitchfork Median-Line Pullback — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Pivot window | 10 bars [j-7, j+2], confirmed at centre+2 | The spec's "confirmed 10-bar pivots (pivot recorded at confirmation bar centre+2)". |
| Schiff anchor | (A bar, (A+B)/2); median line through the B-C midpoint | The Schiff definition; the whole point of the variant vs Andrews. |
| Touch band | low/high within 0.5 ATR(14) of the median line | The spec's touch definition, verbatim. |
| Touch arm | 5 bars after a touch | Staleness guard, not in the source; set a priori so a touch that does not reclaim promptly stops counting. The touch bar itself can trigger if it closes back across the line. |
| Set expiry | 200 bars after C confirms | The spec's expiry, verbatim. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Pivots need 10 bars to confirm and a triple needs ~30 bars to form; 60 gives margin. |

## Spec decisions / ambiguities

1. **The 10-bar pivot window is read as [j-7, j+2].** A pivot
   cannot be confirmed at centre+2 if its test required bars
   beyond centre+2, so the 10-bar window must end at the
   confirmation bar: 7 bars before the centre, 2 after. This is
   the only causal reading of "10-bar pivot, confirmed at
   centre+2".
2. **No minimum swing between consecutive pivots.** The spec
   gives none, and none was imposed — unlike andrews_pitchfork,
   which requires 0.9x ATR between pivots. Consecutive pivots
   of the same kind keep only the more extreme one. The
   consequence is visible in the backtest: forks re-anchor
   constantly and the system trades 1,597 times. Adding a
   minimum swing would be a different system, not a calibration
   of this one.
3. **"Touch from above" is a band, not a side test.** The low
   must be within 0.5 ATR of the median-line value in either
   direction (|low − median| ≤ 0.5 ATR). A low more than 0.5 ATR
   below the line is a break through the line, not a touch from
   above, and does not arm the setup.
4. **The touch bar can trigger.** "Touches ... and then closes
   back above" is read as allowing the same bar to do both (low
   touches, close recovers above the line), as well as a later
   bar within the 5-bar arm.
5. **The far parallel is the exit, through C.** For a long, the
   lower parallel runs through C (the most recent swing low);
   a close below it exits. For a short, the upper parallel runs
   through C (the most recent swing high).
6. **A new triple replaces only its own side's set.** A bearish
   triple completing does not disturb the active bullish set,
   and vice versa.

## What the exits actually did

Shipped run (1,597 trades): 828 signal exits (close beyond the
far parallel or opposite signal) and 769 stop/trail exits — the
exits fire about evenly, so the loss is an entry problem, not an
exit problem.

No bug fixes requiring re-runs, no PnL-selected tuning.
