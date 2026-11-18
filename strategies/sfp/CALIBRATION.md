# Swing Failure Pattern (SFP) — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Swing pivot | 5-bar, centre+2 confirmation | The spec's pivot definition; the standard fractal pivot. |
| Pivot tie rules | High: strictly > both left neighbours, >= both right neighbours; Low: mirror | The spec's exact tie-breaking; equal highs/lows on the right do not invalidate a pivot. |
| Volume spike | v > 1.5x SMA(volume, 20) | The spec's threshold (thrive.fi). The SMA includes the current bar's volume, per the spec as written. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Pivot confirmation needs 5 bars; SMA(20) + ATR(14) need ~20 bars; 60 gives margin. |

## Spec decisions / ambiguities

1. **The swept level is read as of bar i-1.** The spec says
   "l[i] < swing_low as of bar i-1" for the sweep and "c[i] > that
   same swing low" for the reclaim; the shipped code uses the
   shifted level for both, and for the exits too ("c[i] < swing_low
   (the swept level fails again)" is the swept level, i.e. the
   level as of bar i-1). A pivot confirming on bar i itself can
   never be swept and reclaimed by that same bar.
2. **Volume SMA includes the current bar.** "v[i] > 1.5 *
   SMA(v, 20)[i]" is read literally: the 20-bar SMA ending on bar
   i, current volume included. A 1.5x spike against a 20-bar mean
   that includes the spike itself needs roughly a 1.6x multiple
   against the prior 19 bars.
3. **Exits use the swept level, not the latest level.** If a new,
   lower swing low confirms after entry, the long exit still keys
   off the swept (higher) level — the level the trade was predicated
   on — rather than the new low.
4. **Harness stop/trail as an additional exit.** The spec's exits
   are the re-failure through the swept level / opposite SFP; the
   batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar
   max hold) is applied on top, per the batch instruction.

## What the exits actually did

Shipped run (617 trades): 325 trades ended on a signal exit and
292 on the harness stop/trail (BTC 101 signal / 95 stop, ETH 125 /
105, HYPE 99 / 92). The re-failure exit fires about as often as
the stop, i.e. roughly half of all SFP trades close back through
the swept level before the 2xATR stop is reached — the sweep
usually keeps going rather than reversing, which is consistent
with the strategy losing on all three coins.

No bug fixes requiring re-runs, no PnL-selected tuning.
