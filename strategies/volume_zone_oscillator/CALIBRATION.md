# Volume Zone Oscillator — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Signed volume R | sign(close_t − close_{t−1}) × volume_t; 0 if close unchanged, 0 on first bar | Khalil & Steckler's published VZO definition. |
| VP / TV EMA period | 14 | Published VZO smoothing (EMA 14 of signed volume and of volume). |
| VZO formula | 100 × VP / TV, bounded [−100, +100]; TV == 0 → VZO = 0 | Published formula; the zero-volume guard is the only addition (undefined otherwise). |
| Trend EMA | EMA(60) of close | Khalil's published trend context. |
| ADX period / threshold | 14 / > 18 | Khalil's published trend context (ADX(14) > 18 confirms a trend worth trading). |
| Oversold / overbought levels | −40 / +40 | Khalil's published VZO reversal levels. |
| Failed-pullback lookback | 10 bars | Published rule: VZO crosses 0 while the last-10-bar extreme never reached the oversold/overbought level. Window is the trailing 10 bars ending on bar i (inclusive); since the crossing bar itself is past 0, the inclusive/exclusive choice only matters for the 10th-back bar. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| Risk / leverage / costs | 1% risk per trade, 3x leverage cap, 0.045% fee + 0.01% slippage per side | Batch-standard risk layer. |
| WARMUP | 80 | Indicator warmup (EMA(60) + ADX(14) + margin). |

No spec deviations: the signed-volume EMA ratio, the EMA(60)/ADX(14)
trend context, the ±40 reversal crosses, the failed-pullback 0-cross
rule, and the VZO-0 / EMA(60) exits are all implementable exactly as
specified on 24/7 crypto data (no session gaps involved). The
implementation was verified against hand-computed cases: flat closes
give VZO = 0 exactly; steady +1 closes with constant volume give
VZO → 100; alternating ±1 closes give VZO alternating ±50/7
(EMA(14) steady state, alpha = 2/15); zero volume gives VZO = 0 with
no crash; VZO stays inside [−100, +100] on a random walk.

No bug fixes requiring re-runs, no PnL-selected tuning.
