# New York Open Momentum — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| NY open | 13:00 UTC fixed | The spec's "NY open fixed at 13:00 UTC (winter/GMT reading)". 13:00 UTC = 08:00 EST, the NYSE open in winter; in summer (EDT) the NYSE opens 13:00 UTC as well (09:30 EDT = 13:30 UTC), so a fixed 13:00 UTC clock rule is a simplification either way — documented, not tuned. |
| First-hour range | high/low of the 13:00 UTC bar | The spec's "high/low of the 13:00 UTC bar (13:00-14:00)". |
| Break window | UTC hours [14, 17) | The spec's "during the 14:00-17:00 UTC window", read as the three 1h bars opening 14:00, 15:00, 16:00. |
| First break per day per side | yes | The spec's "only the first break of the day per side". |
| Time exit | 21:00 UTC bar close | The spec's "close of the 21:00 UTC bar"; the harness executes the exit signal at the next bar's (22:00) open, so the fill is one bar later than the idealized exit. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 48 bars | Batch-standard risk layer; 48-bar max hold per the spec. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | The pattern needs one day's 13:00 bar plus ATR warmup; 60 gives margin. |

## Spec decisions / ambiguities

1. **13:00 UTC is a clock rule, not a real open.** Crypto trades
   24/7; there is no New York open. The strategy imposes the
   traditional session clock on crypto, exactly as the spec directs.
2. **The range is only visible from 13:00.** Bars earlier in the day
   carry NaN for `ny_high` / `ny_low`; the first-hour range of a day
   never leaks into that day's earlier bars.
3. **A missing 13:00 bar means no trades that day.** If the 13:00
   bar is absent from the frame (a data gap), the day has no range
   and no break can fire.
4. **Opposite break exits, same-bar priority.** A short break on a
   bar exits an open long (and vice versa); the opposite break also
   enters the new side on the next bar's open, per the harness.
5. **Harness stop/trail as an additional exit.** The spec's exits
   are the 21:00 time exit / opposite break; the batch-standard
   risk layer (2xATR stop, 2.5xATR trail, 48-bar max hold) is
   applied on top, per the batch instruction.

No bug fixes requiring re-runs, no PnL-selected tuning.
