# Linear Regression Channel — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Window N | 50 bars | Spec. ~2 days on 1h bars: long enough for a stable OLS fit, short enough to adapt to regime shifts. |
| Band width | 2 × residual std (population, ddof=0) | Spec. The standard 2-sigma band width; population std matches the "std of residuals over the window" wording. |
| Fit variable | Closes vs in-window bar index | Spec. Raff channels are fitted on closes; index regression gives the trend line's end value directly. |
| Entry | Cross outside a band | Spec. A close strictly outside the band is the overextension signal; touches without a cross do not trigger. |
| Exit | Cross back across the midline | Spec. The trend line is the mean-reversion target; exiting there banks the reversion without waiting for the opposite band. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 55 | Spec minimum: 50-bar window + 5 margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
