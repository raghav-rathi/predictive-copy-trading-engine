# HalfTrend — Calibration

No parameter sweep was run and parameters were fixed before seeing
backtest results. Every value below is either the published default of
the source indicator or the batch-standard risk layer.

| Parameter | Value | A priori rationale |
|---|---|---|
| amplitude | 2 | The HalfTrend indicator's published default; the most responsive setting, matching the source exactly. |
| channelDeviation | 2 | The indicator's published default; sets the channel width to ATR(100). Channels are documented only, not traded. |
| ATR period | 100 | Fixed by the HalfTrend specification (atr2 = ta.atr(100) / 2). |
| stop_atr_mult | 2.0 | Batch-standard risk layer. |
| trail_atr_mult | 2.5 | Batch-standard risk layer. |
| target_atr_mult | None | No fixed target; exits are trend flips, stops, trails, or max hold. |
| max_hold_bars | 120 | Batch-standard risk layer (5 days on 1h bars). |
| risk_frac | 0.01 | Batch-standard risk layer (1% equity per trade). |
| max_leverage | 3.0 | Batch-standard risk layer. |
| fee_rate / slippage_rate | 0.00045 / 0.0001 | Batch-standard Hyperliquid taker cost assumption. |
| WARMUP | 110 | ATR(100) lookback plus the amplitude-2 window and margin. |

No parameter was tuned, adjusted, or re-chosen after any backtest run.
