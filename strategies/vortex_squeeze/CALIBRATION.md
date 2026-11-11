# Vortex Squeeze — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Vortex window | 14 | Botes & Siepman default; identical to `vortex`. |
| Bollinger length / multiplier | 20 / 2.0 | Bollinger's own defaults. |
| BandWidth | (upper - lower) / middle | Normalised width, so the squeeze threshold is scale-free across coins. |
| Squeeze percentile window | 120 bars | ~5 days of hourly bars: long enough for a stable percentile, short enough to adapt to regime. |
| Squeeze percentile | 20th | Standard squeeze definition: width in the bottom fifth of its recent range. |
| Gate extension | 5 bars after squeeze ends | Lets a cross that fires on the expansion out of the squeeze count; the expansion, not the compression itself, is the tradeable move. |
| Entry / exit | VI cross + open gate; exit on the opposite VI cross | Per spec; exits are ungated so a position is never held through a flipped trigger. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 150 | BandWidth needs 20 bars and its 120-bar percentile needs 120 of those (first defined ~bar 139); 150 gives margin. |

## Spec deviations

None. The spec is implemented exactly: VI(14) cross, BandWidth(20,2)
below its 120-bar 20th percentile, gate open during the squeeze or
within 5 bars after it ends, exit on the opposite cross. One
interpretation worth noting: "within 5 bars after squeeze ends" is
implemented as a 6-bar rolling max of the squeeze flag (current bar +
previous 5), so a cross fires if any of the last 6 bars was a squeeze
bar.

No bug fixes requiring re-runs, no PnL-selected tuning.
