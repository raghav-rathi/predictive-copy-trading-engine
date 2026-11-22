# Buyable Gap-Up — Calibration

All parameters were fixed **a priori** from the published BGU
specification and 1h-bar reasoning — there is no in-sample sweep,
so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Gap threshold | ≥ 0.75×ATR(40) | the method's own gap size, measured against ATR(40) through the prior bar so the threshold is known at the open |
| ATR length | 40 bars | the method's own ATR length for sizing the gap |
| Volume threshold | ≥ 1.5× average volume | the method's own high-volume condition |
| Volume average | 1,200 bars | 50 trading days × 24 bars on 1h — the method's 50-day average volume, scaled |
| Trend filter | price above SMA(50) and SMA(200) | the method's "uptrend or constructive consolidation"; the 200-bar SMA is the downtrend exclusion |
| Gap-bar stop | gap bar's intraday low/high | the method's own stop — a close below the gap day's low means the gap failed |
| 10-day exit | close below SMA(240) | the method's 10-day moving-average violation, scaled 10 days × 24 bars. **Simplification:** the original uses the 10-day violation only if the stock respected the 10-day for ≥ 7 weeks, else the 50-day violation; we always use the 10-day equivalent and document it |
| Max hold | 240 bars (~10 days) | a BGU that has not run in ten days was not a BGU |
| Harness stop | 2×ATR(14) | backstop only — the signal-level gap-low exit is the real stop |
| Trail / target | none | the method exits on the gap failure or the 10-day violation, not on a trail or target |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 1,250 bars | 1,200-bar volume average + margin |

## Deviations from the source, stated plainly

1. **No true overnight gap in crypto.** Crypto trades 24/7, so
   the 1h open-vs-prior-close gap is the adaptation. Qualifying
   gaps will be much smaller and rarer than equity overnight
   gaps; expect few triggers (see BACKTEST.md).
2. **10-day exit simplified.** Always the 240-bar SMA violation,
   without the original's 7-week respect condition.
3. **Short mirror is builder-added.** The BGU is long-only; the
   gap-down mirror is our symmetric extension.
4. **1h scaling.** Every "day" in the original becomes 24 bars;
   a 50-day volume average on 1h bars is a much longer memory
   than on daily bars.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers — least of all the 0.75×
gap threshold, which directly controls how many trades fire.
