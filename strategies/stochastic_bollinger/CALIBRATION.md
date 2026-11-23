# Stochastic + Bollinger %b — Calibration

All parameters were fixed **a priori** from the published
specification — there is no in-sample sweep, so there is
nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Bollinger | (20, 2) | Bollinger's own standard band parameters |
| %b oversold / overbought | < 0.2 / > 0.8 | Bollinger's %b extremes: price at the band, not merely below/above the mid-band (0.5) |
| Stochastic | (14, 3, 3) | the textbook slow Stochastic: 14-bar range, 3-bar %K smoothing, 3-bar %D |
| %K oversold / overbought | < 30 / > 70 | the standard Stochastic oversold/overbought levels (tighter than the common 20/80 — see note below) |
| Entry | %K cross of %D + double gate | the cross is the timing trigger; the gates are the location filter |
| Long exit | %b > 0.8 or %K cross below %D | the reversion is complete at the opposite band; a %K rollover means momentum failed first |
| Harness stop | 2×ATR(14) | backstop only — the signal-level exit is the real exit |
| Trail / target | none | the opposite band IS the target, enforced in signals.py; a trail would fight the mean-reversion exit |
| Max hold | 120 bars (~5 days) | a reversion that has not happened in five days was not a reversion |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 40 bars | Bollinger(20) + Stochastic(14,3,3) need 20 bars; margin for the smoothings and the cross to form |

## Notes and spec corrections surfaced while implementing

1. **%K gate 30/70, not 20/80.** The task spec fixes %K < 30 /
   %K > 70, which is tighter than the 20/80 levels many
   textbooks quote for Stochastic. 30/70 is the level Bollinger
   himself pairs with %b work and the level the spec pins, so
   it ships as specified; it was not chosen by backtest.
2. **Seeding is a design decision, not a default.** %b is
   undefined for the first 19 bars and when the band width is
   zero; %K/%D are undefined for the first 13 bars and when the
   14-bar range is zero. All are seeded to their neutral values
   (%b 0.5, %K/%D 50.0) so no signal can fire on seeded data
   and no NaN reaches the signal columns. A flat market seeds
   to neutral rather than to an extreme — the honest choice,
   since a flat market is neither oversold nor overbought.
3. **No trend filter, by design.** The published setup has
   none, and the backtest shows the cost of that absence in a
   trending window (see BACKTEST.md). Adding an ADX or
   SMA-trend filter would be a different strategy; it is not
   adopted here to rescue the numbers.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — least of all
the 0.2/0.8 %b gates, which directly control how many trades
fire.
