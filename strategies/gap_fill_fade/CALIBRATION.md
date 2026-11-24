# Gap Fill Fade — Calibration

All parameters were fixed **a priori** from the classic
gap-fill specification and 1h-bar reasoning — there is no
in-sample sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Gap definition | gap = open[i] − close[i−1] | the open-to-prior-close jump, the only gap a 1h bar can show |
| Gap threshold | \|gap\| > 0.5 × ATR(14), strict | half an ATR of dislocation is a real jump, not hourly noise; strict so exactly 0.5 ATR is not a signal |
| ATR for the threshold | ATR(14) at bar i (Wilder, through bar i's close) | the signal is evaluated at bar i's close, so bar-i ATR is causal; using the prior bar's ATR would understate the gap bar's own volatility |
| Fill level | prev_close | the prior bar's close is the level a fill must reach — the textbook definition of a filled gap |
| Entry | on the gap bar itself, one fade per gap | the gap is known by the close; a second gap bar while a fade is held does not re-enter |
| Exit | fill (close >= / <= prev_close) OR opposite gap | the fill is the target; the opposite gap is the reversal exit |
| Stop | 2×ATR(14) | standard volatility stop — the fade is wrong if price runs 2 ATR the wrong way |
| Trail / target | none | the fill exit is the target; a trail would fight the mean-reversion logic |
| Max hold | 24 bars (~1 day) | a 1h gap that has not filled within a day is not filling on this timeframe |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 30 bars | ATR(14) seeding (14 bars) plus margin |

## Deviations from the source, stated plainly

1. **Hourly bars, not daily.** Bulkowski's gap statistics are
   daily-session-break gaps on equities. Crypto trades 24/7,
   so a 1h "gap" is a single hourly jump, not a session
   break. The backtest shows the consequence: 25 gaps in
   eight months, and only 9 of 25 fill within a day.
2. **ATR-relative threshold, not absolute.** The literature
   discusses gaps in price terms; this system normalizes by
   ATR(14) so the same rule works across BTC (~$70k–$120k),
   ETH, and HYPE without per-coin thresholds.
3. **Fill checked from the bar after entry.** A fill that
   already happened on the gap bar itself does not exit the
   trade, because the position only exists from the next
   bar's open. This is an execution-model consequence, not a
   rule change — but it means a gap that fills intraday on
   the gap bar is still held into the next bar.
4. **ATR at bar i, not bar i−1.** The gap bar's own true
   range includes the gap, so bar-i ATR is slightly larger
   than the pre-gap ATR and the 0.5 ATR threshold is
   slightly harder to clear. The alternative (prior-bar ATR)
   would make the threshold easier and fire more trades; the
   choice is documented here, not tuned.

## Spec corrections surfaced while implementing

- **Boundary strictness.** The spec says "gap > 0.5*ATR" and
  "gap < -0.5*ATR" — strict inequalities. A gap of exactly
  0.5 ATR fires no signal, verified by a dedicated boundary
  test with ATR pinned at exactly 2.0.
- **ATR seeding vs gap flags.** Before ATR(14) is defined
  (first 13 bars), gap comparisons against NaN are False, so
  no gap can fire in the seeding window. `gap_atr` is seeded
  to 0.0 there; `atr14` itself keeps its NaN.

No optimization was performed, and the window in BACKTEST.md
must not be used to tune any of these numbers — least of all
the 0.5 ATR threshold or the 24-bar max hold, which directly
control how many (few) trades fire.
