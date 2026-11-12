# ADX + RSI Combo — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| ADX length | 14 | Wilder's standard ADX length; the published ADX+RSI pairing uses 14. |
| RSI length | 14 | Wilder's standard RSI length; the published pairing uses 14. |
| ADX trend threshold | > 25 | The standard "confirmed trend" line in the source (0–25 weak/range, 25–50 strong). |
| Long entry | RSI crosses above 30 with ADX > 25 | Oversold exit as the momentum trigger, per spec. |
| Short entry | RSI crosses below 70 with ADX > 25 | Mirror of the long rule. |
| Long exit | RSI crosses below 50 | Momentum fades back through the midline; no ADX condition, so the exit fires even while the trend is still "strong". |
| Short exit | RSI crosses above 50 | Mirror of the long exit. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 30 | ADX(14) needs 14 bars of Wilder smoothing plus a second smoothing pass for the DX average; 30 gives margin. |

## What the exits actually did

91 of 308 trades (29.5%) ended on the RSI-50 signal exit and 217
on the harness stop/trail — the midline exit is a real, working
mechanism here, not decorative. The stop still dominates because the
2xATR stop is closer than the 50-cross on most losing trades.

## Spec ambiguities

1. **ADX evaluated on the cross bar, not required to be rising.**
   Some sources ask for ADX rising as well as above 25. The spec as
   written says only "ADX(14) > 25", so the shipped version uses the
   level on the cross bar with no rising condition.
2. **No +DI/-DI direction condition.** The source's long checklist
   also prefers +DI above -DI. The spec pins the entry to the RSI
   cross plus the ADX level only, so no DI condition is applied.
3. **Exit at the 50 cross, not at RSI re-entering 30/70.** The spec
   is explicit: exit long on RSI crossing back below 50. A trade
   entered on the 30-cross therefore exits on the first 50-cross,
   which can be a few bars later in a fast move.

No bug fixes requiring re-runs, no PnL-selected tuning.
