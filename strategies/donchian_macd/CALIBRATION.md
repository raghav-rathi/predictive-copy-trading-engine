# Donchian MACD — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Donchian window | 20 bars | The spec's channel length; the standard Donchian window. |
| MACD fast / slow / signal | 12 / 26 / 9 | The spec's MACD parameters; the standard MACD setting. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Donchian needs 21 bars (20 + shift), MACD(26,9) needs ~35 bars to seed; 60 gives margin. |

## Spec decisions / ambiguities

1. **The Donchian channel excludes the current bar.** The spec
   says "close breaks above the trailing 20-bar high (incl.
   current bar)". Read literally with the close, that can never
   fire: the trailing high including the current bar is always
   >= the close, since the bar's high >= its close. The shipped
   reading — the standard Donchian breakout — is the high/low of
   the previous 20 bars (rolling window shifted by 1). The
   "(incl. current bar)" phrasing is preserved for the *high/low
   series* only in the sense that the window rolls through the
   current bar on the next bar; the breakout comparison itself
   must use the prior bars, or the strategy trades zero times.
   This is the one material interpretation in this strategy and
   it is flagged here rather than silently shipped.
2. **Histogram sign is strict.** Histogram exactly 0 confirms
   neither side; a flip is a strict sign change past 0.
3. **Exits use the same channel definition.** "Close below the
   trailing 20-bar low" is the previous-20 low, consistent with
   the entry definition.
4. **Harness stop/trail as an additional exit.** The spec's exits
   are the opposite-channel break / histogram flip; the
   batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar
   max hold) is applied on top, per the batch instruction.

## What the exits actually did

Shipped run (711 trades): 469 trades ended on the harness
stop/trail and 242 on a signal exit (BTC 158 stop / 85 signal,
ETH 159 / 58, HYPE 152 / 99). The histogram-flip / opposite-break
exit fires often, but it does not save the trades — most
breakouts reverse into the 2xATR stop before the exit signal
turns, which is consistent with 20-bar breakouts on 1h crypto
being mostly false breakouts.

No bug fixes requiring re-runs, no PnL-selected tuning.
