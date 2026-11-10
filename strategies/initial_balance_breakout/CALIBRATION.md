# Initial Balance Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Session / IB bar | First 1h bar of each UTC day (00:00–01:00 UTC) | Adaptation of Steidlmayer's first-hour IB to 24/7 crypto; UTC day is the session. |
| IB levels | IB high/low = that bar's high/low, fixed all day | Book definition of the Initial Balance. |
| IB range | IB high − IB low | Book definition; the 1x extension unit. |
| Long entry | First bar after the IB bar (01:00–13:00 UTC) whose close is above the IB high | Closed-bar breakout; the book trades the break of the IB extreme. |
| Short entry | First bar after the IB bar (01:00–13:00 UTC) whose close is below the IB low | Mirror of the long rule. |
| First side wins / one trade per day | After any entry signal, no new entry signals until the next UTC day | Spec rule; prevents re-entry churn after a reclaim exit. |
| Entry window | Signal bars 01:00–13:00 UTC only | Spec rule; no entries in the late session. |
| Long exit | Close back below the IB high, or close at/above IB high + IB range | Reclaim = idea wrong; 1x extension = book's measured-move target. |
| Short exit | Close back above the IB low, or close at/below IB low − IB range | Mirror of the long exits. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 23 bars | Batch-standard risk layer; max hold 23 bars ≈ one session, keeping the trade intraday-ish. |
| Risk / leverage / costs | 1% risk, 3x cap, 0.045% fee + 0.01% slippage per side | Batch-standard risk layer. |
| WARMUP | 30 | ATR(14) warmup + margin. |

## Spec deviations / adaptations (documented, not silent)

1. **Stop is ATR-based, not the far side of the IB.** The book's stop
   is the opposite side of the IB (long stop below the IB low). The
   harness uses a 2.0x ATR stop with a 2.5x ATR chandelier trail
   instead; the IB logic is carried by the signal exits (reclaim of
   the broken level, 1x extension target). This is the documented
   adaptation required by the batch-standard risk layer.
2. **IB bar fallback.** If a UTC day has no 00:00 bar in the frame
   (missing bar), the day's first available bar is used as the IB bar.
   In the shipped backtest window every day has its 00:00 bar, so this
   never fires there; it exists only so synthetic/short frames do not
   crash.
3. **Position carried past midnight.** The book's trade is intraday,
   but the harness has no day-end exit and `max_hold_bars=23` can
   carry a position into the next UTC day. A simulated position
   carried past midnight keeps evaluating exits against the *new*
   day's IB levels — in practice the new day's IB high/low almost
   always triggers the reclaim exit on the first bar, which acts as
   an effective session close. Entries remain gated to one per day
   and only when the simulated position is flat.
4. **No volume / acceptance filter.** The book's full method uses
   Market Profile acceptance (time spent / volume at a level) to
   confirm a breakout. That needs tick-level profile data the 1h
   cache does not have, so the shipped version trades the raw
   closed-bar break with no confirmation filter.

No bug fixes requiring re-runs, no PnL-selected tuning.
