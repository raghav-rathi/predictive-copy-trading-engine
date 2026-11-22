# Multi-Timeframe EMA Agreement — Calibration

All parameters were fixed **a priori** from the BotLab study
and 1h-bar reasoning — there is no in-sample sweep, so there
is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| 1h EMA fast / slow | 9 / 21 | canonical fast/slow trend pair for the base cross |
| 4h EMA fast / slow | 9 / 21 | same pair on the higher timeframe, so the filter tests the same trend at a slower speed |
| 4h resampling | UTC-anchored 4h buckets, last 1h close; only completed bars used | point-in-time discipline: a 4h bar is read only after its final 1h close (see indicators.py) |
| Entry | 1h cross + 4h agreement | the study's surviving filter, verbatim in structure |
| Exit | opposite 1h cross | filter is an entry gate only, as in the study |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 3xATR | trend-following room: the trail rides the move the cross identified |
| Max hold | 120 bars (~5 days) | a cross that has not paid in five days is noise |
| Risk | 1% / trade, 3x leverage cap | house standard |

## Documented deviations / gaps vs the source

1. **EMA lengths are builder-chosen.** The BotLab article
   states the filter as "both the fast pair and the slow pair
   pointing the same way" on 4h but does not publish the EMA
   lengths. 9/21 was chosen as the canonical fast/slow pair and
   applied identically on 1h and 4h. A different pair (e.g.
   8/21, 12/26, or a second slower pair) would be a different
   strategy; the choice was made before seeing the backtest.
2. **Base signal differs from the study's.** The study applied
   the filter to five existing trade lists (a 15m/30m voting
   scalp, a 4h mean-reversion bot, a daily Donchian breakout).
   Here it gates a 1h EMA cross — a new base the study never
   tested. The filter's t ≈ 2.86 therefore does not transfer
   to this implementation; it is a reason to test, not evidence
   for this base.
3. **Funding/OI filters deliberately omitted.** The study found
   they added nothing as entry filters (84–100% agreement);
   implementing them would add complexity with no expected
   signal value. They remain valid as guardrails, which this
   harness does not model.
4. **No funding in this backtest.** The study's costs included
   funding; this run models fees + slippage only. Direction of
   bias: small, and it flatters shorts in positive-funding
   regimes.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — picking the EMA
pair that makes BTC positive on this window would be exactly
the multiple-testing error the source study warns about.
