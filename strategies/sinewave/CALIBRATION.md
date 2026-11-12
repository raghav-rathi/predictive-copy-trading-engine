# SineWave — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Price input | Median price (h + l) / 2 | Ehlers' standard input for his cycle indicators. |
| Detrender | Ehlers high-pass filter, 40-bar cycle | Ehlers' roofing-filter detrender from his DSP work; alpha1 = (1 - sin(2*pi/40)) / cos(2*pi/40). Removes the trend so the Hilbert transform sees a cycle, not a drift. |
| Hilbert transform | Causal FIR Hilbert transformer, 51 taps, Hamming window | Ideal impulse response h[n] = 2/(pi*n) for odd n, 0 for even n, centred at tap 25 (group delay 25 bars). A finite causal approximation of the ideal (infinite, non-causal) Hilbert transform — the only way to keep the indicator causal on live bars. |
| In-phase component | Detrended price delayed 25 bars | Aligns I with Q, which carries the filter's 25-bar group delay. |
| Phase | atan2(Q, I), NaN until bar 50 | Instantaneous phase of the detrended cycle; needs the full 51-tap window. |
| SineWave / LeadSine | sin(phase), sin(phase + pi/4) | Ehlers' pair verbatim (TA-Lib HT_SINE: outSine, outLeadSine). |
| Phase sign convention | H{sin} = -cos, so measured phase = cycle phase - 90 deg | The ideal Hilbert transform sends cos -> sin and sin -> -cos. The constant -90 deg offset does not affect the sine/lead-sine crosses. Verified on synthetic data: on a pure 30-bar sine the unwrapped phase advances at exactly 2*pi/30 per bar. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 100 | 51-tap Hilbert window + high-pass filter spin-up, with margin. |

## Spec deviations

1. **Direct instantaneous phase, not Ehlers' homodyne discriminator.**
   Ehlers' full HT_SINE estimates the dominant cycle period with a
   homodyne discriminator (smoothed Re/Im of consecutive phasors)
   and derives the phase from that estimated period. This build uses
   the direct instantaneous phase atan2(Q, I) of the FIR Hilbert
   transform, as the spec prescribes ("Hilbert transform on
   detrended price → instantaneous phase"). The direct phase is
   noisier — it rotates at the energy-weighted frequency of whatever
   is in the detrended series, including high-frequency noise —
   which is a large part of why the backtest overtrades (9,298
   trades). The homodyne variant would be a different strategy, not
   a parameter choice.
2. **FIR Hilbert transformer instead of Ehlers' 7-tap coefficients.**
   Ehlers' EasyLanguage Hilbert code uses a short 7-tap transformer
   (coefficients 0.0962 / 0.5769). This build uses a 51-tap
   Hamming-windowed ideal response, which has a flatter passband
   and better quadrature accuracy across cycle lengths; the 7-tap
   version was not used because its frequency response is poor
   away from its design frequency. Fixed before seeing results.
3. **Harness stop/trail as the practical exit.** Ehlers' system
   exits on the opposite cross alone. The batch-standard risk layer
   (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on top,
   per the spec's own instruction. In practice 8,375 of 9,298
   trades still end on the signal exit, so the stop/trail is not
   what drives this result — the cross rule itself is.

No bug fixes requiring re-runs, no PnL-selected tuning.
