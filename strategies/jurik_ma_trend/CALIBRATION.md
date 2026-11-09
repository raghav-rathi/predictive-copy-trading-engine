# Jurik MA Trend — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| JMA length | 14 | Spec. |
| JMA phase | 50 (phase_ratio 2.0) | Spec. |
| JMA power | 2 (alpha = beta^2) | Public reconstruction default. |
| JMA construction | Three-stage: adaptive EMA → phase-weighted Kalman detrender → Jurik filter; seeded e0 = JMA = first close, e1 = e2 = 0 | Public reconstruction (Wickra docs; Forex-Station three-stage form). |
| Entry | close crosses above/below JMA AND JMA rising/falling | Spec. |
| Exit | cross back across the JMA | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No spec corrections were needed: length 14 / phase 50 and the
cross + JMA-slope entry rules are implementable exactly as
specified. One honest caveat, also in the README/BACKTEST: Jurik's
original algorithm was never published, so this is the public
three-stage reconstruction (beta/alpha/phase_ratio form verified
against the Wickra docs and the Forex-Station three-stage
description) — results are for this reconstruction, not for
proprietary JMA parity.

No bug fixes requiring re-runs, no PnL-selected tuning.
