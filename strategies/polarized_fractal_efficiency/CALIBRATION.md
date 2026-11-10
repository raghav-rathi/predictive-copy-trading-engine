# Polarized Fractal Efficiency — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Lookback N | 10 | Hannula's PFE lookback (TASC Jan 1994). |
| Straight-line distance | sqrt((close_t − close_{t−10})^2 + 10^2) | Direct n-bar distance; each bar counts as 1 unit on the x-axis. |
| Path distance | sum over i=1..10 of sqrt((close_{t−i+1} − close_{t−i})^2 + 1) | Summed single-bar step distances. |
| Raw PFE | 100 * sign(close_t − close_{t−10}) * straight / path; sign +1 if close_t >= close_{t−10}, else −1; path == 0 → 0 | Hannula's exact formula. |
| Smoothing M | 5 (EMA, span 5, adjust=False) | Hannula's smoothing; first PFE at bar 14 (raw from bar 10, EMA min_periods 5). |
| Entry extremes window | 20 bars | Spec: minimum/maximum PFE over the last 20 bars. |
| Entry extreme level | ±30 | Spec: long requires 20-bar min < −30; short requires 20-bar max > +30. |
| Peak-exit level | ±50 | Spec: exit on a cross back through +50 (−50) after exceeding it since entry, or a cross back through 0. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 40 | Indicator warmup (14 bars to first PFE + margin). |

## Spec deviations / implementation notes

1. **Flat-price quirk (formula as written, not a bug):** on a perfectly
   flat series straight = 10 and path = 10, so raw PFE = +100, not 0.
   The indicator only reads near 0 when the path is much longer than
   the straight-line distance (large choppy swings). This is a direct
   consequence of Hannula's formula as specified; it is implemented
   exactly and locked in by `test_indicator_values_flat`.
2. **Peak tracking starts at the entry-signal bar:** Hannula's exit is
   "after having exceeded +50 at any point since entry". The harness
   executes an entry signal at bar i+1's open, but the signal frame
   only knows the entry-signal bar i, so the stateful scan tracks the
   peak from bar i. In practice the gap is negligible (PFE is an
   EMA(5), so it cannot jump from ~0 to above +50 in one bar), but it
   is an approximation, not the literal fill-bar peak.
3. **Rolling extremes use min_periods=20:** the 20-bar min/max are NaN
   until 20 valid PFE values exist, so no entry can fire before bar 33.
   This is stricter than a partial-window minimum and is causal either
   way.
4. No other deviations: the straight/path/raw/EMA computation follows
   the spec bar-for-bar, verified against hand-computed values
   (linear trends ±100, a +10 jump raw = 74.2374171097, alternating
   ±5 chop raw = 19.6116135138).

No bug fixes requiring re-runs, no PnL-selected tuning.
