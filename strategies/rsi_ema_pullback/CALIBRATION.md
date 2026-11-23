# RSI pullback to EMA(50) — Calibration

All parameters were fixed **a priori** from the Connors/Raschke
pullback rules and 1h-bar reasoning — there is no in-sample
sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| EMA length | 50 bars | the trend filter — price above/below a 50-bar EMA defines the trend |
| Trend definition | close above a *rising* EMA(50) (up) / below a *falling* EMA(50) (down) | requiring the EMA itself to be rising, not just price above it, keeps the filter from firing in flat chop |
| RSI length | 14 bars | Wilder's RSI, the standard pullback oscillator |
| Oversold arm | RSI < 40 | the pullback — RSI has dipped into the lower band while the trend holds |
| Overbought arm | RSI > 60 | the mirror in a downtrend |
| Entry trigger | RSI crosses back above 40 (long) / below 60 (short) | the recovery — the dip is over and momentum is turning back with the trend |
| Long exit | RSI ≥ 70 OR close below EMA(50) | take the bounce at overbought, or admit the trend is gone |
| Short exit | RSI ≤ 30 OR close above EMA(50) | mirror |
| Opposite flip | none | a short setup firing while long does not flip the position; the long's own exits decide (in practice the short setup needs a downtrend, which already means close < EMA(50), so the long exit fires anyway) |
| Harness stop | 2×ATR(14) | backstop only — the signal exits are the real exits |
| Trail / target | none | the exit is the RSI round-trip, not a trail or target |
| Max hold | 120 bars (~5 days) | a pullback bounce that has not reached RSI 70 in five days was not a bounce |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 60 bars | EMA(50) needs 50 bars to exist, plus margin |

## Deviations from the source, stated plainly

1. **Armed state is builder-added.** Connors/Raschke describe
   "RSI pulls back, then turns up." We formalize it as: the
   dip arms the setup, the cross fires it, and the trend must
   still hold at the cross. A dip that breaks the trend
   disarms — the setup is void, not deferred.
2. **The dip need not occur entirely inside the trend.**
   Arming requires the trend on the dip bar itself, but the
   cross is judged on the trend at the cross bar. In practice
   this distinction rarely matters: a dip deep enough to push
   RSI below 40 usually breaks EMA(50) first.
3. **1h scaling.** *Street Smarts* is written for daily bars.
   On 1h bars the EMA(50) is a ~2-day average, far more
   sensitive to a single pullback than a 50-day EMA — which is
   why the filter strangles the setup (3 trades in eight
   months; see BACKTEST.md).

## Spec corrections surfaced while implementing

- **The EMA filter kills most setups — by design, and it is
  the headline finding.** Verified on synthetic data: a -8/bar
  dip after a +1/bar rise pushes RSI below 40 but also breaks
  EMA(50), so no entry fires; only a shallow -2/bar dip keeps
  the trend and enters. This is not a bug — it is the filter
  doing exactly what the spec asks. The 0-trade HYPE result
  and the 3-trade total are the honest outcome of the spec on
  1h crypto, not a defect to fix by loosening rules.
- **RSI seeding:** base.rsi returns 0 on flat/zero-delta
  stretches (no gains, no losses). Early bars therefore read
  RSI 0, which would arm a long if the trend were up — but
  trend_up is False until EMA(50) exists, so no setup can fire
  before WARMUP. Documented, not changed.
- **No flip on the opposite setup** (see table above): the
  task does not specify a flip for this strategy, so none is
  implemented.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — least of all
the 40/60 RSI band or the EMA(50) length, which directly
control how many trades fire.
