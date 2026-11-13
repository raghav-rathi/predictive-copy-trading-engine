# Climax Reversal — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Climax window | 20 bars | New 20-bar high/low defines the extreme; round-number window from the spec, long enough to be a real extreme on 1h bars. |
| Volume multiple | > 2x trailing mean volume | The spec's climax threshold: a genuine volume spike, not ordinary fluctuation. Strictly greater (exactly 2.0x is not a climax). |
| Volume mean | Previous 20 bars (shifted by 1) | The current bar's own spike must not dilute the mean it is compared against; the causal, standard reading of "trailing mean". |
| Close position | Lower third (<= 1/3) / upper third (>= 2/3) of the bar's range | The spec's effort-without-result test: the close gives back at least two-thirds of the bar's range. Thirds are the canonical VSA/Wyckoff close-location split. |
| Exit | Opposite climax | Per spec: a long opened on a selling climax exits on a buying climax, and vice versa. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | 20-bar window + volume-mean shift + margin. |

## Spec deviations

1. **Volume mean excludes the current bar.** The spec says
   "volume > 2x the trailing 20-bar mean volume". Including the
   spike bar itself in the mean would raise the bar for its own
   detection (a 2.5x spike would read as ~2.38x against a mean that
   includes it). The shipped code compares against the previous
   20 bars, which is the standard reading and is documented here.
2. **Close thirds are inclusive bounds.** A close exactly at the
   1/3 or 2/3 line counts as in that third; the boundary is a
   measure-zero event on real data.
3. **Harness stop/trail as an additional exit.** The spec's exit is
   the opposite climax; the batch-standard risk layer (2xATR stop,
   2.5xATR trail, 120-bar max hold) is applied on top, per the
   batch instruction. Climaxes are rare, so most trades will end
   on the stop/trail/max-hold before an opposite climax appears.
4. **Source citation.** The task suggested the LuxAlgo no-demand /
   no-supply page only if relevant; it describes a different
   (narrow-spread, low-volume) pattern, so it is not cited. The
   Wyckoff climax reference used is the verified Wyckoff-method
   guide at patternswizard.com, which documents SC/BC and the
   effort-vs-result law directly.

No bug fixes requiring re-runs, no PnL-selected tuning.
