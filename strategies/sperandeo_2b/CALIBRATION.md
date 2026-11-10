# Sperandeo 2B False-Breakout Reversal — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| 20-bar extreme lookback | 20 bars | Sperandeo's 2B: the false breakout is against a new 20-bar high/low. |
| Minimum pullback | 3 bars | Spec: at least 3 bars of pullback with no new 20-bar extreme before the breakout bar can count. |
| Breakout bar | close beyond the 20-bar extreme | Spec: the breakout bar closes above the 20-bar high (top) / below the 20-bar low (bottom). |
| Failure bar (signal) | close below breakout bar's low / above its high | Spec: that close is the 2B signal. |
| Pattern reset | newer 20-bar extreme, or a fired 2B | Spec: only the most recent qualifying extreme is tracked; state resets once a 2B fires or a newer extreme forms. |
| ATR window / stop / trail | 14 / 2.0x / 2.5x | Batch-standard risk layer. |
| Target | 10.0x ATR | Sperandeo suggests up to 5x the stop; 5x the 2.0x ATR stop distance = 10.0x ATR. |
| Max hold | 120 bars | Batch-standard risk layer. |
| Risk frac / max leverage | 1% / 3.0x | Batch-standard risk layer. |
| Fee / slippage | 0.045% / 0.01% per side | Hyperliquid base taker fee + slippage. |
| WARMUP | 40 | 20-bar lookback + ATR(14) warmup + margin. |

## Spec deviations

1. **Stop placement (approximated).** Sperandeo's stop goes above the
   false-breakout high (for a short) / below the false-breakout low
   (for a long). The batch-standard harness only supports an ATR
   stop, so the stop is 2.0x ATR from entry instead of the
   pattern-defined level. The 2.0x ATR stop is the same order of
   magnitude as the distance from a typical 2B entry to the
   false-breakout high/low, but it is not the same level — a
   pattern-exact stop would require harness changes.
2. **Breakout bar vs. newer-extreme reset (ordering).** The breakout
   bar usually prints a new 20-bar high itself (its high exceeds the
   old extreme), so while armed with >= 3 pullback bars the breakout
   check runs before the newer-extreme reset. Without this ordering
   the pattern could never complete. This follows from the spec's
   own definitions, not from any PnL observation.
3. **No failure timeout.** The spec gives no time limit for the
   failure close after the breakout bar, so the awaiting-failure
   state persists until either the failure close fires or a new
   20-bar extreme beyond the breakout bar's extreme invalidates the
   pattern. A timeout would be an invented parameter.

No other spec corrections were needed: the 20-bar extreme, 3-bar
pullback, breakout-bar close, and failure-bar close rules are all
implementable exactly as specified on 24/7 crypto data (no session
gaps involved). The implementation was verified against hand-built
frames: a 2B Top fires exactly on the failure bar (and only there),
a 2B Bottom is the exact mirror, a breakout attempt with only 2
pullback bars does not count, and a newer extreme restarts the
pullback count.

No bug fixes requiring re-runs, no PnL-selected tuning.
