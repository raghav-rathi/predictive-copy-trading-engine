# Judas Swing — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Asian range | prior evening, UTC hours [20, 24) | The spec's "Asian range = high/low of bars 20:00-00:00 UTC (4 bars, prior evening)". |
| London window | UTC hours [7, 10) | The spec's "07:00-10:00 UTC" read as the three 1h bars opening 07:00, 08:00, 09:00. |
| Sweep | wick beyond the range (l < asian_low / h > asian_high) | The spec's "low sweeps below asian_low (wick)". |
| Reclaim | close back inside the range | The spec's "then a close back above asian_low". |
| Structure shift | close beyond the highest high / lowest low printed since the sweep bar | The spec's "close above the highest high printed since the sweep low". |
| Entry deadline | hour < 12 | The spec's "entries valid only until 12:00 UTC". |
| One signal per day per side | yes | The spec's "one signal per day per side max". |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 48 bars | Batch-standard risk layer; 48-bar max hold per the spec. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | One full UTC day of session state plus ATR warmup; 60 gives margin. |

## Spec decisions / ambiguities

1. **The "since sweep" extreme excludes the sweep bar.** The
   highest high / lowest low is tracked over bars *after* the sweep
   bar, before the current bar. The sweep bar's own high is not
   counted: the shift must beat highs printed after the sweep low
   was made. A trigger therefore needs at least one intervening bar
   after the sweep (a same-bar sweep + reclaim + shift cannot fire).
2. **Sweep and reclaim may straddle the 10:00 window end.** Only the
   sweep itself must occur inside the London window; the reclaim
   and the structure-shift close may occur any time after the sweep
   up to the 12:00 entry deadline. This is the reading that makes
   the 12:00 deadline meaningful.
3. **A deeper sweep before any reclaim restarts the pattern.** If a
   later bar in the window prints a lower low (bullish) before any
   reclaim close, the sweep extreme moves to that low and the
   "since sweep" extreme restarts. After a reclaim, the sweep
   extreme is frozen (it is the exit invalidation level).
4. **The Asian range is the prior evening's, available from 00:00.**
   Bars before 00:00 on the first day in the frame carry NaN and
   can never trigger; this is causal (the evening bars are complete
   before the range is used).
5. **Exits use the most recent sweep level.** The invalidation level
   is the last sweep extreme (`last_bull_sweep_low` /
   `last_bear_sweep_high`, forward-filled). If a newer sweep forms
   while a trade is open, the level updates to the newer sweep.
6. **Harness stop/trail as an additional exit.** The spec's exits
   are the opposite-Judas signal / sweep invalidation; the
   batch-standard risk layer (2xATR stop, 2.5xATR trail, 48-bar
   max hold) is applied on top, per the batch instruction.

No bug fixes requiring re-runs, no PnL-selected tuning.
