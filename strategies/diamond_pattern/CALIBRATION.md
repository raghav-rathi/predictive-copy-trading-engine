# Diamond Pattern — Calibration

All parameters fixed a priori from the textbook diamond
description. No in-sample sweep, nothing selected on the backtest
window.

| Parameter | Value | Rationale |
|---|---|---|
| Pattern length | 15–40 bars | shorter is noise, longer is no longer one formation |
| Min phase | 5 bars each | expansion and contraction must each be a real phase, not a bar or two |
| Expansion | apex range > 1.3x start range | a visible broadening, not a rounding error |
| Contraction | end range < 0.7x apex range | a visible narrowing before the break |
| Shape checks | highs rising / lows falling into the apex, reversed out of it | the diamond's geometry, not just its range profile |
| Volume filter | > 1.2x pattern average | textbook confirmation: breakouts need participation |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for a sharp breakout to run |
| Target | none | the opposite-breakout exit manages the trade |
| Max hold | 168 bars (~7 days) | a diamond breakout that hasn't run in a week was not one |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the expansion/contraction multipliers (1.3x /
0.7x) control the trade count almost entirely — loosening them
floods the strategy with random widening-then-narrowing windows,
and the HYPE leg's 14.8% win rate suggests the current
definition already admits too many of those.

**Verdict: loser.** -$376 combined over 97 trades, with a
coin-split book (ETH green, HYPE deeply red). Do not trade this
as shipped.
