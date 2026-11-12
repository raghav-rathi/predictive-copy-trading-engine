# Swing Failure Pattern — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Swing window | 20 bars, prior bars only (excl. current) | Standard swing lookback; the current bar is excluded so the level is known before the bar trades. |
| Breakout test | high > prior 20-bar high / low < prior 20-bar low | Strict inequality; touching the level exactly is not a breakout. |
| Failure window | 3 bars after the breakout bar, breakout bar included | Per spec: close back inside within the next 3 bars; the breakout bar itself counts because a poke-and-close-back candle is the canonical failure form. |
| One pending failure per side | First close back inside consumes the breakout; newer breakout supersedes a pending one | Prevents duplicate entries off a single breakout. |
| Exit | Opposite failure signal, plus harness stop/trail | Per spec: exit on the opposite failure. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 30 | 20-bar swing window needs 20 bars; 30 gives margin. |

## Spec deviations

1. **The breakout bar itself counts toward the 3-bar window.**
   The spec says "closes back below that swing high within the next
   3 bars". Read strictly, that could exclude the breakout bar
   itself, but the canonical swing-failure candle pokes above the
   level and closes back below it on the same bar — excluding it
   would discard the pattern's most common form. The shipped version
   allows failure on the breakout bar and the next 3 bars (4 bars
   total from the breakout). This choice was fixed before seeing
   results.
2. **Harness stop/trail as the practical exit.** The pattern's native
   exit is the opposite failure, which is rare. The batch-standard
   risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is
   applied on top, per the spec's own instruction, so most trades
   end on the stop/trail rather than the opposite failure.

No bug fixes requiring re-runs, no PnL-selected tuning.
