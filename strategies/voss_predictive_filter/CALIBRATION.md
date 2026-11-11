# Voss Predictive Filter — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Band-pass period | 20 bars | Ehlers' published default (`VossPredictor.Series(Close, 20, 3)`). |
| Bandwidth | 0.25 | Published `once Bandwidth = .25` in the TASC Aug 2019 EasyLanguage. |
| Predict | 3 bars | Published default; Order = 3 * Predict = 9. |
| Voss scale | (3 + Order)/2 = 6 | Published `Voss = ((3 + Order)/2) * Filt − SumC`. |
| SumC weights | ((Count+1)/Order) over Voss lags 1..9 | Published loop; lag 1 carries weight 9/9, lag 9 carries 1/9. |
| Filt seed | 0 for the first 6 bars | Published `if CurrentBar > 5 then Filt = ... else Filt = 0`. |
| ADX gate | ADX(14) < 25 on entries only | Per the batch brief. The Wealth-Lab Traders' Tip text says "25–30" and its code uses `< 30`; the brief fixed 25, the stricter end of the published range. Exits are ungated. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Covers the 20-bar cycle, the 9-bar Voss history, and ADX(14) convergence with margin. |

## Spec deviations

1. **The "band-pass line" is the Filt recursion itself.** The brief
   describes the signal as "Voss crossing above the band-pass filter
   line". The published system plots two lines: Filt (the 2-pole
   band-pass output) and Voss. The Wealth-Lab tip's lagging line is
   `BandPass.Series(Close, 20)`, whose recursion is identical in form
   to Filt (same 2-pole structure, same period/bandwidth
   parameterisation), so Filt is used directly as the band-pass line
   rather than running a second, near-duplicate filter.
2. **ADX threshold 25, not 30.** See the ADX row above: the brief
   fixed 25; the Wealth-Lab code uses 30 and its text allows 25–30.
   25 is the stricter published end and was fixed before seeing results.

No bug fixes requiring re-runs, no PnL-selected tuning.
