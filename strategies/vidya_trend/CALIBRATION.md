# VIDYA Trend — Calibration

No parameter sweep was run and parameters were fixed before seeing
backtest results. Every value below is either the published VIDYA
specification or the batch-standard risk layer.

| Parameter | Value | A priori rationale |
|---|---|---|
| CMO period | 9 | Short momentum window, a standard short-period CMO choice; measures trend strength over the last 9 close-to-close changes. |
| EMA period | 20 | Standard medium EMA period; sets the maximum responsiveness via F = 2/(20+1). |
| F | 2/21 | Fixed by the EMA(20) smoothing-factor formula, not a free choice. |
| alpha | F * \|CMO\| / 100 | Chande's specification verbatim: smoothing scales linearly with absolute trend strength. |
| flat-window CMO | 0 | UpSum + DnSum == 0 means no movement; CMO = 0 by definition, so VIDYA freezes. |
| stop_atr_mult | 2.0 | Batch-standard risk layer. |
| trail_atr_mult | 2.5 | Batch-standard risk layer. |
| target_atr_mult | None | No fixed target; exits are opposite crosses, stops, trails, or max hold. |
| max_hold_bars | 120 | Batch-standard risk layer (5 days on 1h bars). |
| risk_frac | 0.01 | Batch-standard risk layer (1% equity per trade). |
| max_leverage | 3.0 | Batch-standard risk layer. |
| fee_rate / slippage_rate | 0.00045 / 0.0001 | Batch-standard Hyperliquid taker cost assumption. |
| WARMUP | 30 | CMO(9) lookback plus margin for the recursion to settle. |

No parameter was tuned, adjusted, or re-chosen after any backtest run.
