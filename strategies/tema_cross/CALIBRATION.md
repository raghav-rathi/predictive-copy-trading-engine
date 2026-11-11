# TEMA Cross — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| TEMA fast | 9 | Short TEMA length from the spec; fast enough to react on 1h bars while still smoothing noise. |
| TEMA slow | 21 | Slow TEMA length from the spec; the classic 9/21 fast/slow pair. |
| TEMA formula | 3*EMA1 - 3*EMA2 + EMA3 | Mulloy's definition, identical to `tema_trend`. |
| Entry / exit | Cross of TEMA(9) vs TEMA(21); exit on the opposite cross | The cross IS the system; no additional filter by design. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | TEMA(21) needs 21 bars of EMA spin-up three times over (nested EMAs); 60 bars gives margin. |

## Spec deviations

None. The spec is implemented exactly: TEMA(9) vs TEMA(21) cross,
exit on the opposite cross, no regime filter. The only deliberate
difference from `tema_trend` is the absence of the SMA200 filter and
the faster 9/21 lengths, both per the spec.

No bug fixes requiring re-runs, no PnL-selected tuning.
