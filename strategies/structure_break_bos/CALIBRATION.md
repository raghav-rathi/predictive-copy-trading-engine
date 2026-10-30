# Structure Break (BOS) — Calibration

All parameters fixed a priori from the market-structure
definition. No in-sample sweep, nothing selected on the
backtest window's PnL.

| Parameter | Value | Rationale |
|---|---|---|
| Pivot width | 5 bars (2 each side) | per the batch spec; a swing needs bars on both sides to be a swing |
| Pivot confirmation | after the 2 right-hand bars close | no lookahead: an unconfirmed pivot is not a level |
| Break definition | close beyond the level, not a wick | the standard BOS rule: wicks through a level are sweeps, not breaks |
| Entry filter | break in the same direction as the last break | BOS continuation: the trend must already have broken once in this direction, so the entry confirms a higher high / lower low leg, not a first break |
| Exit | opposite structure break (close beyond the most recent opposite swing) | the CHoCH: the structure that defined the trend has failed |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for a trend leg to develop |
| Target | none | the opposite-break exit manages the trade |
| Max hold | 120 bars (~5 days) | trend legs get a long leash |
| Risk | 1% / trade, 3x leverage cap | house standard |

**Sensitivity note:** the entry filter (second consecutive
break) roughly halves the trade count versus entering on
every break, by construction — first breaks are trend
establishment, not continuation. The 120-bar hold never
binds (0 max-hold exits); the stop is the binding exit
(351 of 433), so stop placement, not hold length or the
exit rule, is the lever if this were ever revisited — but
it is not revisited on this window.

**Verdict: no demonstrated edge.** +$283 combined over 433
trades (Sharpe 0.18, win rate 32.8%) is noise. Do not trade
this as shipped.
