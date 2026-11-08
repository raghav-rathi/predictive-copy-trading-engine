# Fast Stochastic Crossover — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| %K window | 14 bars (including current bar) | Spec: %K(14). |
| %D | SMA(3) of %K | Spec. |
| Oversold / overbought | %K < 20 / %K > 80 | Spec. |
| Trend filter | Close above/below SMA(200) | Spec. |
| Zero-range guard | HH14 == LL14 → %K = 50 | Spec; avoids NaN/inf on flat bars. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 250 | SMA(200) warmup + margin. |

Spec interpretation decisions (no tuning involved):

- A cross is strict: %K above %D on bar i with %K ≤ %D on bar
  i−1 (mirror for crosses below). The zone condition (%K < 20 /
  %K > 80) is evaluated on bar i's %K.

No bug fixes requiring re-runs, no PnL-selected tuning.
