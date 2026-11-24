# Heikin Ashi + Stochastic — Calibration

All parameters were fixed **a priori** from the classic
Heikin Ashi / Stochastic specifications and 1h-bar reasoning
— there is no in-sample sweep, so there is nothing to select
on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Heikin Ashi | ha_close=(o+h+l+c)/4, ha_open=(prev ha_open+prev ha_close)/2, seeded ha_open[0]=o[0] | StockCharts ChartSchool recursion; the seed washes out within a few bars and WARMUP=60 covers it |
| Trend filter | EMA(50) of ha_close | a 50-bar average of the smoothed HA close — the trend must agree with the cross, not just the candle colour |
| Stochastic | (14,3): %K raw ratio, %D = SMA(3) of %K | the spec's explicit formulas; Lane's classic 14-bar lookback with a 3-period signal line |
| Oversold / overbought | %K < 30 long / %K > 70 short | cross out of the outer 30% of the range — the standard "buy the bounce from oversold" trigger, tightened from the usual 20/80 to fire slightly more often |
| Entry | transition-only state machine | a cross fires once per position; repeated crosses while holding do not re-enter |
| Exit | opposite %K/%D cross | the momentum rollover — no threshold on the exit, so positions close as soon as %K turns back through %D |
| Stop | 2×ATR(14) | standard volatility stop behind the cross exit |
| Trail | 3×ATR(14) chandelier | safety net for gap-through-cross moves |
| Max hold | 60 bars (~2.5 days) | a stochastic bounce that has not paid within 2.5 days was not a bounce |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 60 bars | EMA(50) + 14-bar stochastic window, with margin |

## Deviations from the source, stated plainly

1. **Fast %K, not Slow/Full (14,3,3).** The spec labels the
   oscillator "Stochastic(14,3,3)" but then defines %K as the
   raw ratio and %D as the SMA(3) of %K. That is the Fast
   form: raw %K with a 3-period %D. The Slow/Full (14,3,3)
   form smooths %K itself by 3 first and takes %D as a second
   3-period average — a different, laggier oscillator. The
   spec's explicit formulas govern, so the fast form is what
   is implemented. A slow-stochastic variant would be a
   separate strategy, not a silent swap.
2. **30/70 instead of 20/80.** The classic oversold /
   overbought levels are 20 and 80; the spec fixes 30/70.
   The looser levels fire more often — and still only 47
   trades fired in ~8.3 months, which says the binding
   constraint is the EMA(50) gate, not the threshold.
3. **HA-open seed.** StockCharts seeds the first HA open to
   (o+c)/2 and starts the calculation before the first
   visible bar; the spec fixes ha_open[0] = o[0]. The two
   seeds converge to the same recursion within a few bars
   and WARMUP = 60 covers the difference.
4. **Zero-range %K = 50.** A flat 14-bar window makes the
   ratio 0/0; %K is set to neutral 50.0 rather than 0 or
   100. Untestable on real 1h crypto (ranges are never
   exactly zero), but it keeps %K in [0, 100] with no NaN.
5. **ha_ema50 fill.** `base.ema` leaves the first 49 bars
   NaN; the fill is ha_close itself, so the trend comparison
   is False (equal) before the EMA exists instead of
   leaking NaNs. No entry can fire before bar 49 — covered
   by `test_warmup_no_entries_before_bar_49`.

## Spec corrections surfaced while implementing

- **The long gate is nearly shut (found by testing, not by
  backtesting).** %K < 30 means price is in the bottom 30%
  of its 14-bar range; ha_close > ha_ema50 means price is
  above its 50-bar average. On a random walk those two
  co-occur on only ~7% of bars (59/800 on seed 5, vs 206
  below the EMA), and with the cross timing and the HA-bullish
  filter added, the full long condition fired **zero times
  across six seeded 800-bar random walks** — while the short
  mirror fired 1–4 times per walk. The long path does work:
  a crafted spike (to 115) → pullback (to 103) → bounce
  series fires a long with all four conditions verified at
  the entry bar (`test_long_entry_fires_on_spike_pullback_bounce`),
  and real data produced 20 longs in the batch-45 window.
  The gate was NOT loosened: the spec is the spec, and the
  rarity is reported as a finding, not fixed by tuning.
  Any future variant that wants more longs should relax the
  EMA gate or the %K threshold explicitly, as a new
  strategy — not as a silent edit here.
- **Entries are rare on real data too.** 47 trades across
  three coins in 6,111 bars is ~1 per coin per 5.5 days,
  with shorts outnumbering longs 27 to 20. The backtest
  verdict ("small loser on a tiny sample") follows directly.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — least of all
the 30/70 thresholds or the EMA(50) length, which directly
control how many (few) trades fire.
