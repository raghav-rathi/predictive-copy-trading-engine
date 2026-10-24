# Bollinger %B Band-Tag Reclaim — Calibration

All parameters were fixed **a priori** from the published
Bollinger literature and 1h-bar reasoning — there is no
in-sample sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Bollinger window / width | 20 / 2.0 | Bollinger's canonical defaults; 20 1h bars is under a day, so the band tracks the local regime without over-smoothing |
| Entry levels | 0 / 1 (reclaim) | the tag levels themselves; the cross (not the level) is the trigger, so the trade waits for the reclaim rather than catching the tag |
| Exit level | 0.5 | the middle band — the natural mean-reversion target of a band-tag trade |
| ATR window | 14 | canonical |
| Stop | 1.5×ATR | a tag that keeps running past the band was not a tag, it was a breakout — cut it |
| Trail | 2×ATR chandelier | locks in the legs that extend past the mid-band |
| Max hold | 72 bars (~3 days) | a band tag that hasn't reverted in 3 days is a trend, not a tag |
| Risk | 1% / trade, 3× leverage cap | house standard |

The design bet is that the reclaim filters out falling knives:
a tag that immediately reverses is a trade, a tag that keeps
falling never triggers. The backtest (BACKTEST.md) tests exactly
that bet — and on this window it fails, mostly through the
stop: 605 of 741 trades exit on the stop, not the mid-band
signal, meaning the reclaim usually re-reverses before reaching
0.5. That is a finding about the idea, not a reason to retune
it on this window.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers.
