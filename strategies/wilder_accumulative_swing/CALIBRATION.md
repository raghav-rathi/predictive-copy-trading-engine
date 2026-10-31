# Wilder Accumulative Swing Index — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| SI formula | 50 × ((C − Cy) + 0.5 × (C − O) + 0.25 × (Cy − Oy)) / R | Spec / Wilder via BabyPips. The 0.5 and 0.25 weights are Wilder's own: the current bar's open-to-close move counts half, the prior bar's gap counts a quarter. |
| R variant | max(H − Cy, Cy − L, H − L) | Spec. Guaranteed positive when H > L; R == 0 guard covers only the degenerate flat bar. Documented in README.md. |
| ASI start | ASI = 0 on bar 0, SI from bar 1 | Spec. No prior bar exists for bar 0, so no SI is defined there. |
| Signal line | EMA(ASI, 10) | Spec. A short EMA keeps the crossover responsive; a longer one would lag an already-cumulative index further. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 20 | Spec minimum: 10 bars for the ASI EMA + 10 margin. |

No bug fixes requiring re-runs, no PnL-selected tuning. The heavily
negative backtest (BACKTEST.md) was not tuned upward.
