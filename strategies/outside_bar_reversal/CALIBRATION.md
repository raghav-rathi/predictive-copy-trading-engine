# Outside-Bar Reversal — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| SMA window | 20 | Spec. |
| Volume average | 20 trailing completed bars | Spec. |
| Upper/lower third | Close position ≥ 2/3 (long) / ≤ 1/3 (short) | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

Spec deviation (documented): the spec's exit is "close below the
outside bar's low" (the entry outside bar's low). Implemented
vectorized as a close below the low of the most recent outside bar as
of the prior bar — identical while no newer outside bar has formed
after entry, and it keeps the exit armed on the same level if a newer
outside bar appears. The opposing-outside-bar exit is implemented
exactly as specified.

No bug fixes requiring re-runs, no PnL-selected tuning.
