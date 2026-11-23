# MACD Divergence — Calibration

All parameters were fixed **a priori** from the classic
divergence specification and 1h-bar reasoning — there is no
in-sample sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| MACD | (12, 26, 9) | Appel's classic MACD; the histogram is the Aspray histogram (MACD line minus signal) |
| Pivot window | ±2 bars | a pivot is the strict extreme of a 5-bar window; 2 bars of confirmation is the tightest window that still filters single-bar spikes |
| Pivot strictness | strict lowest/highest | equal lows/highs (flat bars) must not spawn duplicate pivots |
| Entry filter | histogram rising (long) / falling (short) on the confirmation bar | the divergence alone is a setup; the histogram's turn on the confirmation bar is the trigger — without it the entry would fire into still-falling momentum |
| Exit | histogram zero-cross OR opposite divergence | the zero-cross is the momentum-failure exit; the opposite divergence is the reversal exit |
| Stop | 2×ATR(14) | divergence entries are counter-trend (buying a lower low), so the stop is the standard volatility stop |
| Trail / target | none | the exit is the zero-cross or the opposite divergence, not a trail or target |
| Max hold | 120 bars (~5 days) | a divergence that has not turned within five days was not a turn |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 60 bars | 26-bar slow EMA + pivot confirmation, with margin |

## Deviations from the source, stated plainly

1. **MACD-only, no RSI divergence.** The slug says
   `macd_rsi_divergence` but RSI divergence was not
   implemented, per the build spec. RSI(14) is computed for
   inspection only. A genuine RSI-divergence variant would be
   a separate strategy, not a silent addition here.
2. **Regular divergence only.** Hidden divergence (trend
   continuation) is not traded — only the classic reversal
   form.
3. **Histogram-rising entry filter is builder-added.** The
   classic literature trades the divergence itself; requiring
   the histogram to be rising on the confirmation bar is our
   trigger condition, and it is what keeps entries from firing
   while momentum is still falling into the pivot.
4. **1h scaling.** The ±2-bar pivot window is 2 hours of
   confirmation; on daily bars the same rule would use 2 days.
   Pivots (and therefore divergences) fire far more often on
   1h — 402 trades across three coins in eight months.

## Spec corrections surfaced while implementing

- **Pivot seeding on synthetic data.** Deriving the low as
  `min(open, close)` ties adjacent bars (a bar's open equals
  the prior close), which defeats the strict-lowest pivot
  test. Real 1h candles carry genuine intraday lows, so the
  strict test works on real data; the test suite uses explicit
  `l = c - 1` / `h = c + 1` series for this reason. This is a
  test-data artifact, not a signal bug.
- **MACD seeding.** `base.macd` leaves the histogram NaN for
  the first 26 bars; it is deterministically seeded to 0.0
  and WARMUP = 60 covers the window. No signal reads the
  seeded region in the backtest.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — least of all
the ±2 pivot window or the (12, 26, 9) MACD lengths, which
directly control how many trades fire.
