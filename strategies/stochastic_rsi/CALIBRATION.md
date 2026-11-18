# Stochastic RSI Cross — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| RSI length | 14 | The spec's RSI length; the standard RSI setting. |
| StochRSI lookback | 14 | The spec's StochRSI window; matches the RSI length per Chande & Kroll. |
| %K / %D smoothing | SMA(3) / SMA(3) | The spec's smoothing; the standard StochRSI setting. |
| Oversold / overbought gates | 20 / 80 | The spec's levels; the standard StochRSI extremes. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | RSI(14) + 14-bar StochRSI window + 3+3 smoothing needs ~34 bars to seed; 60 gives margin. |

## Spec decisions / ambiguities

1. **Divide-by-zero guard.** When the 14-bar RSI range is 0 (flat
   RSI, e.g. a flat price series), StochRSI is undefined 0/0; the
   spec fixes it to 50.0 (neutral), shipped as written.
2. **The oversold/overbought gate reads the prior bar's %K.**
   The spec says "%K on the prior bar was < 20" (long) / "> 80"
   (short) — shipped literally with `stochrsi_k.shift(1)`. Using
   the current bar's %K would be a different (weaker) gate and
   would let crosses that merely pass through the extreme count.
3. **Exits use strict crosses.** "Crosses above 80" / "crosses
   below 20" are strict crosses via `crossed_above` /
   `crossed_below` against the scalar level, not touches: %K
   merely sitting above 80 does not exit a long.
4. **Harness stop/trail as an additional exit.** The spec's exits
   are the opposite cross / far-level cross; the batch-standard
   risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is
   applied on top, per the batch instruction.

## What the exits actually did

Shipped run (2,166 trades): 1,676 trades ended on a signal exit and
490 on the harness stop/trail (BTC 556 signal / 171 stop, ETH 553 /
165, HYPE 567 / 154). The opposite-cross / far-level exits fire
constantly — %K whipsaws across %D and the 80/20 levels several times
a day on 1h bars — so the signal exit, not the stop, dominates, and
each churned round trip pays fees while the average trade loses $8.18.

No bug fixes requiring re-runs, no PnL-selected tuning.
