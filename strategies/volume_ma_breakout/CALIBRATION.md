# Volume MA Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Breakout window | 20 bars | New 20-bar high/low defines the extreme; round-number window from the spec. |
| Volume multiple | > 1.5x trailing mean volume | The spec's confirmation threshold: a genuine volume spike, not ordinary fluctuation. Strictly greater (exactly 1.5x is not a breakout). |
| Volume mean | Previous 20 bars (shifted by 1) | The current bar's own spike must not dilute the mean it is compared against; the causal, standard reading of "trailing mean". |
| Exit window | 10 bars, prior bars only | The spec's trailing 10-bar low/high. The current bar is excluded: a close can never be below its own bar's low, so an inclusive 10-bar low could never trigger a long exit. |
| Exit comparison | Close strictly below/above | A close exactly at the prior 10-bar low/high does not exit (strict inequality). |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | 20-bar window + volume-mean shift + 10-bar exit window + margin. |

## Spec deviations

1. **Volume mean excludes the current bar.** The spec says
   "volume > 1.5x the trailing 20-bar mean volume". Including the
   spike bar itself in the mean would raise the bar for its own
   detection. The shipped code compares against the previous
   20 bars, which is the standard reading and is documented here.
2. **Exit uses the prior 10 bars, not the trailing 10 including
   the current bar.** An inclusive 10-bar low contains the current
   bar's own low, which is always <= the close, so "close below
   the trailing 10-bar low" could never fire. The shipped exit
   compares the close against the low of the previous 10 bars.
   This is the only reading under which the spec's exit rule is
   operative at all.
3. **New extreme uses >= / <= (ties count).** A high exactly equal
   to the trailing 20-bar high counts as a new high, matching the
   template's climax convention. The boundary is a measure-zero
   event on real 1h data.
4. **Harness stop/trail as an additional exit.** The spec's exit is
   the 10-bar-range break; the batch-standard risk layer (2xATR
   stop, 2.5xATR trail, 120-bar max hold) is applied on top, per
   the batch instruction.

No bug fixes requiring re-runs, no PnL-selected tuning.
