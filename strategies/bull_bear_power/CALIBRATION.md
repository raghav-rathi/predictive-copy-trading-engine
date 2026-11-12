# Bull Bear Power — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| EMA period | 13 | Elder's own period for the consensus value, used by both powers. |
| Bull Power | high - EMA(13) | Elder's formula verbatim. |
| Bear Power | low - EMA(13) | Elder's formula verbatim. |
| Long trigger | Bear Power rising vs prior bar, still < 0, Bull Power > 0 | Elder's buy signal verbatim: negative but rising Bear Power with positive Bull Power. |
| Short trigger | Bull Power falling vs prior bar, still > 0, Bear Power < 0 | Mirror of Elder's sell signal. |
| Exit | Opposite turn, plus harness stop/trail | Per spec: the exit is the opposite turn of the same two conditions. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 30 | EMA(13) needs 13 bars; 30 gives margin. |

## Spec deviations

1. **Harness stop/trail as the practical exit.** Elder's Elder-Ray
   is a confirmation tool with no native exit of its own; the
   shipped system exits on the opposite turn plus the batch-standard
   risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold), per
   the spec's own instruction, so most trades end on the
   stop/trail rather than the opposite turn.
2. **No EMA-slope filter.** Elder pairs the powers with a rising /
   falling EMA(13) as a trend filter in the Triple Screen; the spec
   as written does not include it, so the shipped system trades the
   turn conditions alone. The Bull Power > 0 / Bear Power < 0
   conditions already embed a weak version of the same read.

No bug fixes requiring re-runs, no PnL-selected tuning.
