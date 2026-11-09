# MESA Adaptive Moving Average Crossover

Ehlers MAMA/FAMA: a Hilbert-transform phase-rate adaptive EMA. The dominant cycle's phase advance per bar (measured with a Hilbert transform + homodyne discriminator) sets the EMA smoothing factor alpha, clamped to the fast limit 0.5 / slow limit 0.05. FAMA follows MAMA at half alpha. When the cycle turns fast the average speeds up to ~a 3-bar EMA; in chop it slows to ~a 39-bar EMA and nearly stops moving.

## Rules

- Long: MAMA crosses above FAMA. Exit on MAMA crossing below FAMA.
- Short: MAMA crosses below FAMA. Exit on MAMA crossing above FAMA.
- Price input is (h + l) / 2, Ehlers' original EasyLanguage input.
- All computation is causal, so signals on bar i use only data through bar i's close. ATR stop / trail from the risk layer also applies.

## Source

- John F. Ehlers, "MAMA — The Mother of Adaptive Moving Averages": https://mesasoftware.com/papers/MAMA.pdf
- John F. Ehlers, *Rocket Science for Traders: Digital Signal Processing Applications*, John Wiley & Sons (ISBN 0471405671)
- TA-Lib MAMA reference (formula + defaults): https://ta-lib.org/functions/mama.html

Paper only, no live execution.
