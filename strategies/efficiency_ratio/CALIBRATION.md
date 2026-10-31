# Efficiency Ratio — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| ER period | 10 | Spec; Kaufman's recommended ER period in KAMA(10,2,30). |
| ER threshold | 0.3 | Spec; above the noise floor (sideways ER clusters near 0–0.2) but low enough to admit developing trends rather than only perfect ones. |
| Entry EMAs | 9 / 21 | Spec. Classic fast/slow cross pair. |
| Flat-window ER | 0.0 | Spec; a flat window has no directional efficiency, so it must fail the gate. |
| Exit ER condition | None | Spec; exits follow the opposite cross unconditionally so a position is never trapped by a collapsing ER reading. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 30 | Spec minimum: 21 bars for EMA(21), 11 for ER(10), +9 margin. |

No bug fixes requiring re-runs, no PnL-selected tuning. The mildly
positive backtest (BACKTEST.md) is small enough to be noise; it was not
tuned upward.
