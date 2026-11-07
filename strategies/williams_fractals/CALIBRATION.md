# Williams Fractal Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Fractal | 5-bar, strict high/low vs 2 bars each side, confirmed 2 bars late | Bill Williams fractal definition. |
| Alligator | SMMA(13/8/5) of median price, unshifted | Spec: "use unshifted values" (classic Williams shifts 8/5/3 forward; not applied here). |
| Long filter | Close above teeth, lips > teeth > jaw | Spec: awake, pointing up. |
| Entry | Close crosses the most recent confirmed fractal level with the filter met | Spec. |
| Exit | Reverse fractal break | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No spec corrections, no bug fixes requiring re-runs, no PnL-selected tuning.
