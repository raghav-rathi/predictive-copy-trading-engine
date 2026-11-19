# Value-Area Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Profile bins | 50 across [day low, day high] | The spec's bin count; fine enough that the POC bin is narrow, coarse enough that a day's 24 bars populate it. |
| Value-area coverage | 70% of the day's volume | The spec's value-area definition (the standard 70% convention for value area). |
| POC expansion | add the heavier adjacent bin first (ties expand down) | Standard POC-outward expansion; the tie rule is arbitrary and documented here. |
| Volume assignment | each bar's volume to the bin containing its close | The spec's rule; uses close as the bar's representative price. |
| Acceptance | 2nd consecutive close beyond VAH / VAL | The spec's rule: one close outside is a poke, two is acceptance. |
| Profile timing | prior completed UTC day, available from the new day's 00:00 UTC bar | The spec's no-lookahead rule; the profile never uses the current day's bars. |
| Streak reset | at each UTC day boundary and on any close back inside the area | The levels change each day, so a streak cannot carry across; a close inside breaks acceptance. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Two full days (48 bars) are needed before the first profile exists; 60 gives margin. |

## Spec decisions / ambiguities

1. **Degenerate days.** If a day's range is flat (high == low) or
   its volume is zero, the value area collapses to the day's
   range (VAH = day high, VAL = day low). A close can then only
   trigger by printing strictly outside a flat range.
2. **First (partial) day.** The backtest window starts 22:00 UTC,
   so the first "day" has only 2 bars; its profile (from those 2
   bars) becomes active at the next midnight. That is prior-day
   data, so it is causal, but the profile is thin — a documented
   consequence of the window start, not a fix.
3. **Exits use the active day's levels.** A long exits on a close
   at or below the *current* VAH; if the profile reprices at
   midnight while a trade is open, the exit level moves with it.
4. **No volume weighting by bar range.** Each bar contributes its
   full volume to a single bin (the close's bin), per the spec;
   no attempt is made to spread a bar's volume across the bins its
   range covers.

## What the exits actually did

Shipped run (947 trades): 522 trades ended on a signal exit
(close back inside the value area) and 425 on the harness stop /
trail. The signal exit is the working exit here — the value-area
rejection fires often, which is also why the trade count is high
and the win rate low (27.2%).

No bug fixes requiring re-runs, no PnL-selected tuning.
