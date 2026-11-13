# GARCH Volatility — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| GARCH omega / alpha / beta | 1e-8 / 0.08 / 0.90 | Fixed RiskMetrics-style a priori values from the spec; alpha+beta=0.98 gives a highly persistent but stationary variance process. No MLE fitting was done, so these are not fitted to this window. |
| GARCH seed | omega/(1-alpha-beta) = 5e-7 | The unconditional variance of the recursion; the neutral starting point, not a tuned value. |
| Returns | 1h log returns ln(c_t/c_{t-1}) | Standard GARCH input; the recursion's r_{t-1} term uses the previous bar's return only. |
| Vol percentile window | 1000 bars | Long enough that the 30th/70th percentiles are stable; drives the 1100-bar warmup. |
| Normal band | 30th–70th percentile | The middle 40% of the vol distribution: trade breakouts in ordinary volatility, skip panic spikes and dead calms. Symmetric, round-number band chosen a priori. |
| Breakout window | 20 bars | Canonical Donchian-style breakout length; previous 20 bars excluding the current bar, so the breakout level is known before the close. |
| Exit | Close back inside the 20-bar range | Per spec: below the broken high (long) / above the broken low (short). |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 1100 | 1000-bar percentile window + 20-bar breakout window + margin. |

## Spec deviations

1. **Forecast vol timing.** sigma2_t is computed from r_{t-1} and
   sigma2_{t-1}, i.e. the forecast for bar t uses data through bar
   t-1's close. The percentile band is then evaluated on that
   forecast vol at bar t. This is the only causal reading of the
   recursion as written; a same-bar return would be lookahead.
2. **Breakout level excludes the current bar.** The 20-bar high/low
   is the max/min of the previous 20 bars (shifted by 1), so a close
   above it is a genuine breakout of a level fixed before the bar.
   Using the current bar's own high would make every strong bar a
   "breakout" of itself.
3. **Harness stop/trail as an additional exit.** The spec's exit is
   the close back inside the range; the batch-standard risk layer
   (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on top,
   per the batch instruction.

No bug fixes requiring re-runs, no PnL-selected tuning.
