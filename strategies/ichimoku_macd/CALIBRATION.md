# Ichimoku MACD — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Tenkan / Kijun / Senkou B | 9 / 26 / 52 | The spec's standard Ichimoku parameters, via the shared `strategies.base.ichimoku` helper. |
| Displacement | 26 bars | Standard Ichimoku: Senkou A/B are plotted 26 bars forward. |
| Cloud alignment | Spans AS PLOTTED at bar i (displaced, not shifted back) | The spec's explicit choice. A span value plotted at bar i is computed from Tenkan/Kijun at bar i-26, so it uses only data through bar i-26 and is fully causal at bar i. Shifting the spans back 26 bars (the "current cloud") would instead compare the close against a cloud computed from data through bar i — a different, more reactive test. The shipped reading is the textbook plotted cloud. |
| Chikou span | NOT used | The shared helper computes Chikou as `close.shift(-26)` — 26 bars into the future. Using it would be lookahead. It is not copied into the indicator frame (tested: no `chikou` column). |
| MACD | (12, 26, 9), histogram sign only | The spec's parameters, via the shared `strategies.base.macd` helper; only the histogram's sign is used, not its magnitude or a signal-line cross. |
| "Above/below the cloud" | Strict vs BOTH spans | Long needs close > Senkou A AND close > Senkou B; short needs close < both. NaN spans (before the displacement window fills) compare False, so no entry can fire before the cloud exists. |
| Cloud exit | Close no longer on the cloud's side | Long exit when close <= max(Senkou A, Senkou B) — the close has entered the cloud or fallen below it. Short exit is the mirror (close >= min span). Using max/min handles thick and thin clouds identically. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 120 | The cloud needs 52 bars + 26 displacement = 78 bars before Senkou B exists; 120 covers that plus the Tenkan/Kijun and MACD warmups with margin. |

## Spec deviations

1. **Cloud alignment documented as a choice.** The spec says
   "using the cloud values as known at bar i — i.e. the leading
   span values plotted at bar i, no forward displacement into
   the future". The shipped code uses `base.ichimoku`'s
   `senkou_a` / `senkou_b` exactly as returned — the displaced
   spans plotted at bar i. "No forward displacement into the
   future" is read as: do not project the spans forward beyond
   bar i, and do not use any value computed from data after bar
   i. The alternative reading (unshift the spans back 26 bars so
   they are "current") was NOT shipped; it would be a different
   strategy and was not tested.
2. **Chikou span excluded.** The spec does not mention Chikou,
   and the helper's implementation is lookahead, so it is left
   out entirely rather than "fixed".
3. **Exit is a cross OR a cloud re-entry.** The spec's long exit
   is "Tenkan crosses below Kijun OR close enters the cloud".
   "Enters the cloud" is implemented as "no longer above the
   cloud" (close <= cloud top), which also covers falling
   straight through the cloud — a close below both spans has
   certainly left the long side, and exiting there is the same
   decision.
4. **Harness stop/trail as an additional exit.** The spec's exits
   are the Tenkan/Kijun cross and the cloud re-entry; the
   batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar
   max hold) is applied on top, per the batch instruction. 214
   of 293 trades ended on the stop/trail and 79 on the signal
   exits, so the signal exits do real work here (~27%) but the
   stop still dominates.

No bug fixes requiring re-runs, no PnL-selected tuning.
