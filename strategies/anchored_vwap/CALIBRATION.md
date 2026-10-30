# Anchored VWAP — Calibration

All parameters fixed a priori from the anchored-VWAP
definition in the batch brief. No in-sample sweep, nothing
selected on the backtest window's PnL.

| Parameter | Value | Rationale |
|---|---|---|
| Pivot window | 20 bars centred (10 each side) | the brief's "20-bar swing pivot"; a centred window is the standard swing definition |
| Pivot activation | at bar j + 10 | the right-hand window must be observed before the pivot counts; otherwise the series would look ahead |
| Pre-confirmation fallback | VWAP from bar 0 | keeps the series defined (no NaN) before the first pivot confirms |
| Long entry | close crosses above swing-low AVWAP, AVWAP rising vs 5 bars ago | reclaim of the post-low cost basis with upward slope confirmation |
| Short entry | mirror at the swing-high AVWAP, falling vs 5 bars ago | loss of the post-high cost basis with downward slope confirmation |
| Exit | opposite cross of the same AVWAP | the thesis (price on the profitable side of the anchor cohort's cost) is gone |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | house standard |
| Target | none | the opposite cross manages the trade |
| Max hold | 120 bars (~5 days) | backstop; signal exits dominate in practice |
| Risk | 1% / trade, 3x leverage cap | house standard |

**Why the activation delay matters:** a pivot bar's AVWAP
value is only meaningful once the pivot is confirmed, 10
bars later, by which time price has typically moved well
away from the anchor's typical price. The shipped rule does
not paper over this — it waits for confirmation and takes
the crosses that actually occur afterwards, which is part of
why the trade count (525) is high yet the win rate is low:
many of those crosses are late reclaims inside choppy
retraces rather than fresh trend legs.

**Verdict: loser.** -$5,543 combined over 525 trades
(19.8% win rate). Do not trade this as shipped.
