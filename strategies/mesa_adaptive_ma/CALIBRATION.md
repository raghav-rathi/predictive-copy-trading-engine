# MESA Adaptive Moving Average Crossover — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Price input | (h + l) / 2 | Ehlers' EasyLanguage input Price((H+L)/2) in the MAMA paper. |
| Fast limit | 0.5 | Ehlers' suggested maximum alpha. |
| Slow limit | 0.05 | Ehlers' suggested minimum alpha. |
| Hilbert FIR / homodyne discriminator | 0.0962 / 0.5769 coefficients, (0.075*period + 0.54) factor | Ehlers / TA-Lib `ta_MAMA.c` recursion. |
| Instantaneous period | 360 / atan(Im/Re), clamped [6, 50], smoothed 0.2/0.8 | Ehlers / TA-Lib. |
| FAMA alpha | alpha / 2 on current MAMA | Ehlers: FAMA uses half the MAMA alpha. |
| First-output lookback | 32 bars NaN | TA-Lib initial unstable period for MAMA. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup (32-bar lookback + margin). |

No spec corrections were needed: the Hilbert-transform quadrature,
instantaneous-period, fast/slow-limit alpha, and MAMA/FAMA cross
rules are all implementable exactly as specified on 24/7 crypto data
(no session gaps involved). The implementation was verified against
the published recursion: flat data converges MAMA/FAMA to the flat
price with alpha pinned at the 0.5 fast limit, alpha stays inside
[0.05, 0.5] and period inside [6, 50] on a random walk, and MAMA
sits above FAMA through a steady uptrend.

No bug fixes requiring re-runs, no PnL-selected tuning.
