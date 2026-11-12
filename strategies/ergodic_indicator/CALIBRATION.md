# Ergodic Oscillator — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Momentum | m = close - close[1] | Blau's one-bar momentum, verbatim. |
| First smoothing | EMA(25) | Blau's published long smoothing r = 25. |
| Second smoothing | EMA(13) | Blau's published short smoothing s = 13. |
| Signal line | EMA(ergodic, 7) | Blau's published signal length; 7 is the standard pairing with 25/13. |
| Normalisation | 100 * PC / APC, 0 where APC == 0 | Blau's construction verbatim; flat markets map to 0, not NaN/inf. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Double-EMA(25,13) + EMA(7) spin-up (first finite signal ~bar 43), with margin. |

## Relation to the existing true_strength_index strategy

**Correction to the brief:** the brief described this build as using
"different smoothing lengths — 25/13/7 vs that strategy's
parameters". That is incorrect. Verified against the shipped code
(`strategies/true_strength_index/indicators.py`): the existing TSI
strategy uses exactly the same smoothing lengths — LONG_SMOOTH = 25,
SHORT_SMOOTH = 13, SIGNAL_N = 7 — and the identical double-EMA
formula. Blau's ergodic oscillator and his True Strength Index are
the same construction (the LuxAlgo source confirms: "Identical in
form to William Blau's True Strength Index; TSI defaults r = 25 and
s = 13 are also common"), so no different-length variant exists to
build. The two strategies differ only in the signal rule and the
risk layer:

| | ergodic_indicator (this build) | true_strength_index (existing) |
|---|---|---|
| Oscillator | 100 * EMA(EMA(m,25),13) / EMA(EMA(\|m\|,25),13), signal EMA(7) | Identical |
| Long entry | Raw cross of ergodic above signal | Cross above signal AND ergodic > 0 (zero-territory filter) |
| Short entry | Raw cross below signal | Cross below signal AND ergodic < 0 |
| Exits | Opposite cross | Opposite cross (no territory filter) |
| Stop / trail | 2.0xATR / 2.5xATR (batch-standard) | 1.5xATR / 2.0xATR |
| Warmup | 60 | 120 |

The honest reading of this batch's result is therefore a controlled
comparison: the raw cross (this build) loses -$7,507.50 combined,
and the difference vs the TSI build's result is attributable to the
zero-territory filter and the tighter stop/trail, not to the
oscillator.

## Spec deviations

1. **No zero-territory filter.** The spec prescribes the raw
   signal-line cross, and the shipped build follows it. Blau's
   canonical usage is the raw cross; the zero filter is the TSI
   strategy's own addition and was deliberately not copied here so
   the two builds stay distinct.
2. **Harness stop/trail as the practical exit.** The batch-standard
   risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is
   applied on top of the opposite-cross exit, per the spec's own
   instruction. 797 of 1,467 trades end on the stop, so the stop
   is doing about half the exiting here.

No bug fixes requiring re-runs, no PnL-selected tuning.
