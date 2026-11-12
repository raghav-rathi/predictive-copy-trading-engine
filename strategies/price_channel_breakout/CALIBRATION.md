# Price Channel Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Channel lookback | 30 bars | Shipped spec. The classic Donchian/Turtle setting is 20 bars (System 1) or 55 (System 2); 30 sits between them as the spec's fixed choice — longer than 20 to cut 1h-crypto whipsaw, shorter than 55 to keep trade frequency up. Not tuned on the backtest. |
| Channel bands | Prior 30 bars only, current bar excluded | The breakout close must exceed every high in the completed window; a current-inclusive channel would make the close trivially equal to the band on a new-high bar. |
| Midline | (channel high + channel low) / 2 | The Donchian midline by definition. |
| Exit | Midline cross, plus harness stop/trail | Per spec: exit long on a close back below the midline, exit short on a close back above it; the batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on top. Differs from the Turtle exit (opposite 10-bar breakout) — the spec fixes the midline exit. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | The 30-bar channel needs 30 bars plus the one-bar shift; 40 gives margin. |

## Spec deviations

1. **30-bar channel instead of the classic 20-bar Turtle setting.**
   The spec fixes 30 bars. The 20-bar Turtle System 1 and 55-bar
   System 2 are the published defaults; 30 is a deliberate middle
   choice, fixed before seeing results, and was not selected by
   backtest performance.
2. **Midline exit instead of the Turtle opposite-breakout exit.**
   The Turtles exited System 1 on the opposite 10-bar breakout. The
   spec fixes the midline cross as the exit, which is also a
   documented Donchian usage (the midline as a trailing stop / exit
   level). The shipped system therefore exits earlier than the Turtle
   rule in a retracement.
3. **Harness stop/trail as the practical exit.** The batch-standard
   risk layer is applied on top, per the spec's own instruction, so
   most trades end on the stop/trail rather than the midline cross.

No bug fixes requiring re-runs, no PnL-selected tuning.
