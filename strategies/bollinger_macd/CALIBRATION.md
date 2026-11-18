# Bollinger MACD — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Bollinger period / k | 20 / 2.0 | The spec's Bollinger parameters; the standard setting. |
| MACD fast / slow / signal | 12 / 26 / 9 | The spec's MACD parameters; the standard setting. |
| Band-touch window | 3 bars | The spec's window: the tag may be up to 2 bars before the cross. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Bollinger needs 20 bars, MACD(26,9) ~35 bars to seed; 60 gives margin. |

## Spec decisions / ambiguities

1. **Band touch uses the current bar's band value.** The spec
   says "min(l[i-2..i]) <= bb_lower[i]" — the trailing 3-bar
   low window (which includes the current bar's low) is
   compared against the band value on bar i. The band value
   itself is computed from closes through bar i only, so this
   is causal. An alternative reading (each bar's low vs its
   own band) would need three band values; the shipped reading
   follows the spec's formula literally.
2. **"Touched or pierced" is <= / >=, not strict.** A low
   exactly equal to the lower band counts as a touch.
3. **MACD crosses are strict.** `crossed_above` requires
   macd > signal now and macd <= signal on the prior bar
   (base.py's definition); equality on the prior bar still
   counts as a cross.
4. **Exit on reaching the opposite band is strict.** Close
   exactly on the upper band does not exit a long; it must be
   above it.
5. **Harness stop/trail as an additional exit.** The spec's exits
   are the opposite MACD cross / opposite band; the
   batch-standard risk layer (2xATR stop, 2.5xATR trail,
   120-bar max hold) is applied on top, per the batch
   instruction.

## What the exits actually did

Shipped run (221 trades): 74 trades ended on the harness
stop/trail and 147 on a signal exit (BTC 31 stop / 57 signal,
ETH 23 / 56, HYPE 20 / 34). Unlike the trend strategies, the
signal exit fires first most of the time — the opposite MACD
cross or opposite-band touch closes trades before the stop —
which keeps drawdowns small but also caps winners, leaving a
47.1% win rate with PF 0.88.

No bug fixes requiring re-runs, no PnL-selected tuning.
