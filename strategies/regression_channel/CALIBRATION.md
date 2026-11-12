# Linear Regression Channel — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Regression length | 100 bars | Per spec; the source's 50–100 "balanced / swing trading" band, top end for stability on 1h bars. |
| Band width | ±2.0 × stddev of residuals | Per spec; the standard 2σ channel (covers ~95% of prices if residuals were normal). |
| Residual std | ddof=1 over the same 100 bars | Per spec ("stddev of residuals over the same 100 bars"); pandas-style sample std. |
| Long entry | Close crosses back above the lower band | Per spec: the cross-back, not the touch — price must first reach the band and then return inside it. |
| Short entry | Close crosses back below the upper band | Mirror of the long rule. |
| Exit | Close crosses the regression midline | Per spec: the midline is the mean-reversion target. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 120 | The channel needs 100 bars; 120 gives margin. |

## What the exits actually did

196 of 482 trades (40.7%) ended on the midline signal exit and 286
on the harness stop/trail — the highest signal-exit share in the
batch, so the reversion leg genuinely completes often. The problem
is the entry, not the exit: the midline is reached but the move from
band to midline is too small to cover the 2xATR stop losses on the
trades that never revert.

## Spec ambiguities

1. **No slope / R² trend filter.** The source's mean-reversion
   variant asks for a confirmed trend direction (positive slope for
   longs) before taking the band trade. The spec as written defines
   the entry purely on the band cross-back with no slope condition,
   so no slope filter is applied.
2. **Residuals measured against the current window's line.** The
   spec says "stddev of residuals over the same 100 bars" — the
   residuals are the window's closes minus the line fitted on that
   same window (centered rolling-sum form), not minus each bar's
   own-window line. An early implementation took the rolling std of
   a per-bar residual series, which lagged the band width by an
   extra 100 bars and was replaced before any backtest was recorded.
3. **A cross can fire because the band moved, not because price
   moved.** The bands are recomputed every bar; a cross-back is
   evaluated against the moving band series. That is inherent to the
   spec's "crosses back above the lower band" wording and is kept.

No bug fixes requiring re-runs after the final backtest, no
PnL-selected tuning.
