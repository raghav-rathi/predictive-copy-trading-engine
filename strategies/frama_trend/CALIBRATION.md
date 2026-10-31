# FRAMA Trend — Calibration

No parameter sweep was run and parameters were fixed before seeing
backtest results. Every value below is either the published Ehlers
specification or the batch-standard risk layer.

| Parameter | Value | A priori rationale |
|---|---|---|
| N | 16 | Even lookback (required: N/2 must be integral); a short, responsive window suited to 1h bars, versus the source's daily-bar default of 20. |
| alpha formula | exp(-4.6 * (D - 1)), clamped [0.01, 1] | Ehlers' specification: D = 1 gives alpha = 1 (full responsiveness in a clean trend), D = 2 gives alpha = exp(-4.6) ≈ 0.01 (maximum smoothing in congestion). |
| D clamp | [1, 2] | Fractal dimension of a price series lies in [1, 2] by construction; the clamp guards degenerate windows. |
| zero-range D | 2 | A perfectly flat window carries no trend information, so it is treated as full congestion (slowest adaptation). |
| stop_atr_mult | 2.0 | Batch-standard risk layer. |
| trail_atr_mult | 2.5 | Batch-standard risk layer. |
| target_atr_mult | None | No fixed target; exits are opposite crosses, stops, trails, or max hold. |
| max_hold_bars | 120 | Batch-standard risk layer (5 days on 1h bars). |
| risk_frac | 0.01 | Batch-standard risk layer (1% equity per trade). |
| max_leverage | 3.0 | Batch-standard risk layer. |
| fee_rate / slippage_rate | 0.00045 / 0.0001 | Batch-standard Hyperliquid taker cost assumption. |
| WARMUP | 40 | N = 16 lookback plus margin for the recursion to settle. |

No parameter was tuned, adjusted, or re-chosen after any backtest run.
