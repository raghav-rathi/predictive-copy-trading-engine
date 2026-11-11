# Early Onset Trend — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| High-pass cutoff | 100 bars | Published: the high-pass filter removes cyclic components whose periods are shorter than 100 bars (the roofing filter's spectral-dilation limit). |
| SuperSmoother LPPeriod | 30 bars | Published `LPPeriod(30)` input. |
| K1 / K2 | 0.85 / 0.40 | Published inputs; K1 drives the entry quotient, K2 the exit quotient. |
| Peak decay | 0.991 | Published fast-attack / slow-decay AGC: `Peak = .991 * Peak[1]`. |
| Signal lines | Q1 crosses 0 / Q2 crosses 0 | Published strategy code: buy when Quotient1 crosses over 0, sell when Quotient2 crosses under 0. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Covers the 100-bar high-pass and SuperSmoother(30) settling with margin. |

## Spec deviations

1. **Exact published form implemented — the brief's fallback was NOT
   used.** The brief allowed a fallback (SuperSmoother(10) of median
   price minus its delayed value, trigger = EMA(9)) if the exact
   published recursion could not be verified. It could: the TASC Aug
   2014 Traders' Tips page reproduces Ehlers' EasyLanguage verbatim
   (high-pass → SuperSmoother(30) → peak AGC → quotient transform),
   so the exact form is implemented and the fallback is not needed.
2. **Date correction: August 2014, not 2016.** The brief dates the
   indicator to "TASC 2016". The article is "The Quotient Transform",
   TASC August 2014 (Traders' Tips, Aug 2014). No parameter or logic
   change follows from the date; the 2014 code is the source.
3. **No separate trigger line.** The brief describes "EOT crossing
   above its trigger". The published indicator has no trigger line —
   it has two quotient transforms of the same normalised output, and
   Ehlers' own strategy trades their zero crossings. The mapping used
   here is the published one: long on Q1 crossing above 0, short on
   Q2 crossing below 0, exits on the opposite quotient's zero cross.
   A long exit and a short entry therefore fire on the same bar (and
   vice versa), exactly as in the published strategy.
4. **First-two-bars seeding.** HP/Filt are 0 for i < 2 (the second
   difference needs three closes), matching the EasyLanguage variables
   initialising to 0; X is defined as 0 while Peak is 0.

No bug fixes requiring re-runs, no PnL-selected tuning.
