# ADX / DI Crossover — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| DMI period | 14 | Spec: Wilder DMI(14). |
| ADX entry threshold | > 25, rising | Spec. |
| DI spread at cross | >= 5 | Spec. |
| ADX exit threshold | < 20 | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No spec corrections were needed: the Wilder DMI/ADX computation, the
cross + ADX filter + spread entry rules, and the cross / ADX < 20
exits are all implementable exactly as specified on 24/7 crypto data
(no session gaps involved). The DMI/ADX math reuses the shared
`strategies.base.adx` helper (Wilder smoothing, alpha 1/14), which is
the same construction the spec describes.

No bug fixes requiring re-runs, no PnL-selected tuning.
