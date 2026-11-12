# Stochastic Momentum Index — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Range window | 13 bars | Blau's published SMI default (the 10,3,3 variant on some platforms is a different parameterisation, not used). |
| Double smoothing | EMA(25) then EMA(2) on both D and (HH-LL) | Blau's published defaults; the 25-period first pass is what makes the SMI slow enough to need a 60-bar warmup. |
| SMI scale | 100 * DS / (0.5 * DHL), clamped to [-100, 100] | Blau's formula verbatim; the clamp only binds on degenerate data (DS/DHL slightly over 1 from EMA lag). |
| Entry zones | Cross above -40 / below +40 | Blau's conventional overbought/oversold zones (+40 / -40). |
| Exit | Cross back through 0, plus harness stop/trail | Per spec: the zero line is where closes flip to the other half of the range. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Range window 13 + double EMA(25,2) needs ~30 bars to stabilise; 60 gives margin. |

## Spec deviations

1. **Zero range (DHL = 0) yields SMI 0.** On flat bars the range is
   zero and the ratio is undefined; the shipped code returns 0
   (midpoint, no momentum) instead of NaN, so no spurious entries
   fire on zero-range data.
2. **Harness stop/trail as the practical exit.** Blau's system exits
   on the zero-line cross alone. The batch-standard risk layer
   (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on top,
   per the spec's own instruction, so most trades end on the
   stop/trail rather than the zero-line cross.

No bug fixes requiring re-runs, no PnL-selected tuning.
