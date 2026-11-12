# Keltner Channel Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Mid line | EMA(20) of close | Raschke's ATR-form Keltner standard (20-period EMA). |
| ATR length | 10 | Raschke's ATR-form standard (ATR over 10 periods). |
| ATR smoothing | Wilder (alpha = 1/10) | The shared `strategies.base.atr` primitive is Wilder smoothing by definition; `strategies.base.keltner` uses it. |
| Band multiplier | 2.0 | The standard Keltner multiplier (EMA +/- 2 * ATR). |
| Long entry | close > upper band | Spec verbatim. |
| Short entry | close < lower band | Spec verbatim. |
| Long exit | close < upper band (back inside) | Spec: "exit on close back inside the channel". A close that has fallen back below the upper band is inside (or through) the channel. |
| Short exit | close > lower band (back inside) | Mirror of the long exit. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer (note: the risk layer's ATR(14) is separate from the signal ATR(10)). |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 30 | EMA(20) needs 20 bars; ATR(10) needs 10; 30 gives margin. |

## Spec deviations

1. **Exit is "back inside", not "back to the midline".** Some Keltner
   breakout variants exit on a close back to the EMA(20) midline.
   The spec as written says "exit on close back inside the channel",
   so the shipped exit fires as soon as the close is no longer
   outside the band (long: close < upper band; short: close > lower
   band). This is a fast exit — a breakout that fails to hold the
   band for even one bar exits immediately — and it is the literal
   reading of the spec, fixed before seeing results.
2. **Harness stop/trail as the practical exit.** The batch-standard
   risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied
   on top of the channel-re-entry exit, per the batch instruction.

No bug fixes requiring re-runs, no PnL-selected tuning.
