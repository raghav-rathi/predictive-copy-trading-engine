# MAMA — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Price input | (H + L) / 2 | Ehlers' original MAMA input (EasyLanguage `Price((H+L)/2)`). |
| Smooth | (4P + 3P[1] + 2P[2] + P[3]) / 10 | Ehlers' 4-bar weighted MA pre-filter. |
| Hilbert transformer | 0.0962 / 0.5769 taps on lags 0, 2, 4, 6, × (0.075·Period[1] + 0.54) | Ehlers' 7-tap truncated Hilbert transform, verbatim from the original code / TA-Lib. |
| Instantaneous period | 360 / atan°(Im/Re) from the I2/Q2 homodyne discriminator; walk-clamped [0.67, 1.5]× previous period; clamped [6, 50]; smoothed 0.2·Period + 0.8·Period[1] | Ehlers' original period estimator. Period is used for the Hilbert-transformer scaling factor and is exposed as `mama_period`; it does not set alpha directly (see deviation 1). |
| Phase | atan°(Q1 / I1), one-arg atan, −90..90° | Ehlers' phase; one-arg atan (not atan2) per the original code. |
| DeltaPhase | max(1, Phase[1] − Phase) | Ehlers' phase rate of change; floored at 1° so alpha never exceeds FastLimit. |
| alpha | clamp(FastLimit / DeltaPhase, SlowLimit, FastLimit), FastLimit 0.5, SlowLimit 0.05 | Ehlers' published limits; alpha opens to 0.5 at phase snap-back (every half cycle) and tightens toward 0.05 when phase barely moves. |
| MAMA / FAMA | MAMA = alpha·price + (1−alpha)·MAMA[1]; FAMA = 0.5·alpha·MAMA + (1−0.5·alpha)·FAMA[1] | Ehlers verbatim; FAMA uses half MAMA's alpha. |
| Seed | Period 20, MAMA/FAMA at the first price | Ehlers' code initializes Period at 0 and MAMA/FAMA at 0; seeding at the first price avoids a meaningless ramp from 0, and WARMUP = 100 keeps all spin-up out of the backtest. |
| Exit | Opposite cross, plus harness stop/trail | Per spec: the system reverses on the opposite cross, and the shipped system uses the harness 2xATR stop / 2.5xATR trail as the exit mechanism plus the reverse signal. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 100 | Hilbert chain + period estimator spin-up; TA-Lib's own MAMA lookback is 32 bars, 100 gives margin. |

## Spec deviations and ambiguities

1. **Alpha is FastLimit / DeltaPhase, not "0.15/period" and not
   "FastLimit/period".** The batch brief's mechanism line contains
   two conflicting alpha formulas: "alpha = 0.15/period" and, in the
   same parenthetical, "the standard MAMA alpha = FastLimit/period
   with FastLimit 0.5, SlowLimit 0.05 as published". Neither matches
   any published MAMA: Ehlers' original code and TA-Lib both compute
   alpha = FastLimit / DeltaPhase, where DeltaPhase is the phase rate
   of change in degrees (floored at 1°), clamped to [SlowLimit,
   FastLimit]. The instantaneous period enters only the Hilbert
   transformer scaling, not alpha. The shipped implementation follows
   Ehlers/TA-Lib verbatim. A literal "0.5/period" alpha would sit at
   the 0.05 slow limit almost always (period 6 → 0.083, period ≥ 10 →
   0.05) and reduce MAMA to a near-fixed slow EMA — that is not
   MAMA. This differs from the earlier `mama_fama` strategy, which
   uses a non-canonical period-ratio alpha (DeltaPhase =
   period[i−1]/period[i]); this slug is the canonical phase-based
   version.
2. **Detrender float-hygiene snap.** The Hilbert taps sum to exactly
   zero, so on constant input the detrender is analytically 0, but
   floating-point residue leaves ~1e-14 values that make the phase
   jump around and fire spurious MAMA/FAMA crosses on flat stretches
   (found by the flat-data unit tests). Values with |detrender| <
   1e-12 are snapped to exactly 0.0. That is 7+ orders of magnitude
   below any real detrender value, so real data is unaffected; only
   the exact-zero case is cleaned up.
3. **Lags before bar 0 clamp to bar 0's value** (rather than 0), the
   same convention as the earlier `mama_fama` implementation. This
   only affects spin-up bars, which WARMUP excludes.
4. **Harness stop/trail as the practical exit.** Ehlers' system exits
   on the opposite cross alone. The batch-standard risk layer
   (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on top,
   per the spec's own instruction.

## What the exits actually did

- 603 of 747 trades (80.7%) ended on the harness stop/trail, 144 on
  the opposite-cross signal, 0 on max hold. The MAMA/FAMA cross is
  selective as an entry (747 trades over ~8 months), but once in, the
  2xATR stop usually fires before the cross reverses — the reported
  result is mostly entry selectivity plus the standard stop/trail,
  not a clean MAMA trend hold. BTC is the weak leg (−$2,539.70);
  ETH (+$1,573.70) and HYPE (+$640.97) both clear breakeven but
  neither clears Sharpe 1.

No bug fixes requiring re-runs, no PnL-selected tuning.
