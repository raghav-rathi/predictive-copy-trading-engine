# MAMA

John F. Ehlers' MESA Adaptive Moving Average (*Technical Analysis of
Stocks & Commodities*, Sep 2001; *Cybernetic Analysis for Stocks and
Futures*, 2004): an adaptive EMA whose smoothing alpha is set by the
rate of change of the market cycle's phase, measured with a truncated
Hilbert transform. The chain follows Ehlers' original EasyLanguage
code (as in TA-Lib's TA_MAMA) verbatim:

- **price** = (H + L) / 2
- **Smooth** = (4·P + 3·P[1] + 2·P[2] + P[3]) / 10
- **Detrender** = HT(Smooth), **Q1** = HT(Detrender),
  **I1** = Detrender[3], **jI** = HT(I1), **jQ** = HT(Q1)
- **I2** = 0.2·(I1 − jQ) + 0.8·I2[1]; **Q2** = 0.2·(Q1 + jI) + 0.8·Q2[1]
- **Period** = 360 / atan°(Im / Re) from the homodyne discriminator,
  walk-clamped to [0.67, 1.5]× the previous period, clamped to [6, 50],
  then 0.2·Period + 0.8·Period[1]
- **Phase** = atan°(Q1 / I1) (one-arg atan, −90..90°);
  **DeltaPhase** = max(1, Phase[1] − Phase)
- **alpha** = clamp(FastLimit / DeltaPhase, SlowLimit, FastLimit)
  with FastLimit = 0.5, SlowLimit = 0.05
- **MAMA** = alpha·price + (1 − alpha)·MAMA[1]
- **FAMA** = 0.5·alpha·MAMA + (1 − 0.5·alpha)·FAMA[1]

where HT is Ehlers' 7-tap Hilbert transformer:
HT(x)[t] = (0.0962·x[t] + 0.5769·x[t−2] − 0.5769·x[t−4] − 0.0962·x[t−6])
· (0.075·Period[t−1] + 0.54). FAMA lags MAMA by construction, so
their crossovers signal trend reversals.

## Rules

- **Long entry:** MAMA crosses above FAMA.
- **Short entry:** MAMA crosses below FAMA.
- **Long exit:** MAMA crosses below FAMA (opposite cross).
- **Short exit:** MAMA crosses above FAMA (opposite cross).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  max hold 120 bars.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- John F. Ehlers, "MESA Adaptive Moving Averages", TASC Sep 2001: https://docs.wickra.org/Indicators/Indicator-Mama

Paper only, no live execution.
