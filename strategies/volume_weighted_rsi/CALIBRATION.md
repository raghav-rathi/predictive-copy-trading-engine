# Volume-Weighted RSI — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
A small sweep (2 alternate settings, run and reported honestly below)
was used only to check robustness, not to select the shipped config.

| Parameter | Value | A priori rationale |
|---|---|---|
| Typical price | tp = (h + l + c) / 3 | Standard typical price. |
| VWTP window | 14 bars | Matches the RSI period, so the volume-weighted price and the RSI share one lookback. |
| RSI period | 14 (Wilder smoothing, via `strategies.base.rsi`) | The canonical RSI length. |
| Long / short levels | RSI crosses below 30 / above 70 | Canonical oversold / overbought levels. |
| Exit level | RSI crosses back through 50 | The midline: the oversold/overbought condition has unwound. |
| Zero-volume fallback | VWTP falls back to the plain close when the rolling 14-bar volume sum is exactly 0 | A zero-volume window carries no volume information; the close is the neutral substitute. A window with fewer than 14 bars stays NaN. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | VWTP needs 14 bars and RSI needs 14 more; 40 gives margin — and it matters, see below. |

## Sweep (robustness check only — shipped config unchanged)

| Setting | Combined trades | Win% | Net $ | PF | Fees $ |
|---|---|---|---|---|---|
| **Shipped: VWTP 14, levels 30/70/50** | **510** | **40.0%** | **-4062.61** | **0.84** | **4107.67** |
| Alt A: VWTP 10, levels 25/75/50 | 502 | 40.4% | -4593.94 | 0.81 | 3814.85 |
| Alt B: VWTP 21, levels 35/65/50 | 465 | 36.6% | -4282.85 | 0.81 | 3856.43 |

Both alternates also lose with PF ~0.81. The loss is not a
parameter accident: every nearby setting loses, so the shipped
config was kept as specified.

## Spec decisions / ambiguities

1. **First-valid-RSI cross artifact.** `strategies.base.rsi`
   fills pre-valid values with 0 (100 * (avg gain > 0)), so the
   first genuine RSI value (~bar 27, after the VWTP + RSI
   warmups) registers as a cross from 0 — e.g. a spurious
   short_entry at bar 27 on a rise-then-fall frame. This is a
   property of the shared `rsi` helper, not of this strategy.
   WARMUP=40 means the harness never trades it: the unit test
   asserts no backtest entry occurs before bar 41. Do not "fix"
   this by changing the shared helper.
2. **VWTP includes the current bar.** The rolling 14-bar window
   ends at bar i, so VWTP(i) uses volume through bar i's close —
   causal, no lookahead.
3. **RSI is computed on VWTP, not on close.** When volume is
   constant, VWTP is the 14-bar rolling mean of tp, which smooths
   the RSI input relative to plain close RSI; the strategy is
   therefore not the same as RSI(14) on close.

## What the exits actually did

Shipped run (510 trades): 335 trades ended on the harness stop /
trail and 175 on the RSI-50 signal exit. The stop dominates, which
is why the win rate (40.0%) and profit factor (0.84) both sit
below breakeven on every coin.

No bug fixes requiring re-runs, no PnL-selected tuning.
