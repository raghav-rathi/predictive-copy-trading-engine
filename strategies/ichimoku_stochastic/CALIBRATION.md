# Ichimoku + Stochastic — Calibration

All parameters were fixed **a priori** from the classic
Ichimoku and Stochastic specifications and 1h-bar reasoning
— there is no in-sample sweep, so there is nothing to select
on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Ichimoku | (9, 26, 52), shift 26 | Hosoda's classic lengths; the cloud is the trend filter |
| Stochastic | (14, 3, 3) | Lane's classic Stochastic; %K on closes, %D = SMA(3) of %K |
| Oversold / overbought gates | %K < 30 (long) / %K > 70 (short) | the cross must fire from an extreme, not mid-range |
| Entry | close beyond cloud + Tenkan/Kijun alignment + Stochastic cross from extreme | all three must agree on the same bar — trend, momentum, and timing |
| Exit | opposite Stochastic cross OR close back inside/through the cloud | the cross is the momentum-failure exit; the cloud re-entry is the trend-failure exit |
| Stop | 2×ATR(14) | standard volatility stop |
| Trail | 3×ATR chandelier | protects open profit on the trend leg (rarely reached — median hold 2 bars) |
| Target | none | the exit is the cross or the cloud re-entry, not a target |
| Max hold | 120 bars (~5 days) | a cloud trade that has not run within five days was not a trend leg |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 80 bars | Senkou B needs 52 bars + 26-bar shift = 78 bars before the cloud is formed, plus margin |

## Deviations from the source, stated plainly

1. **Historical cloud, not projected cloud.** The textbook
   plots Senkou A/B 26 bars into the future. This system
   reads the shifted values at the current bar, where they
   derive from data through bar *i*−26 — the only causal way
   to use them. The projected cloud is never read.
2. **Chikou Span omitted.** The textbook's fifth line is
   `close.shift(-26)` in `base.ichimoku` — a 26-bar lookahead.
   It is not computed or exposed, and no signal reads it.
3. **Stochastic on closes, not highs/lows.** The classic %K
   uses the high/low range; this implementation uses the
   close range (lowest/highest closes of 14 bars), per the
   build spec. On 1h crypto the close range is the cleaner
   series (intraday wicks would otherwise dominate %K).
4. **%K clipped to [0, 100].** When the close equals the
   14-bar high, floating-point rounding can produce
   100.00000000000001; the column is clipped to its
   definitional bounds. Flat 14-bar ranges define %K = 50.0
   (neutral) instead of NaN.
5. **1h scaling.** The cloud takes 78 bars (~3 days) to form;
   the Stochastic turns several times a day. The entry gate
   is the binding constraint, and the cloud re-entry exit
   fires within 2 bars on the median trade (see BACKTEST.md).

## Spec corrections surfaced while implementing

- **Stochastic %K overshoot.** The first test run failed the
  0–100 bounds test with %K = 100.00000000000001 — a
  floating-point artifact, not a logic error. Fixed by
  clipping, not by changing the formula.
- **Cloud formation time.** Senkou B is first defined at bar
  77 (52 + 26 − 1), so WARMUP = 80 is the minimum honest
  value; anything lower would trade on a partially formed
  cloud.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — least of all
the %K < 30 / > 70 gates or the cloud re-entry exit, which
directly control how many trades fire and how fast they exit.
