# Donchian + RSI — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Donchian period | 20 bars | Donchian's standard period (one trading month on daily bars); the source uses period 20. |
| Donchian reference | Prior 20 bars, current bar excluded | The standard Donchian definition: the channel is the extremes of the lookback window, and a breakout is the close leaving that window's range. Including the current bar would make every new high a "breakout" by construction. |
| RSI length | 14 | Wilder's standard RSI length; the source uses RSI 14. |
| RSI long threshold | > 55 | Per spec: breakout needs momentum confirmation above the 55 midline-plus level (not the classic 70, which would almost never fire on a fresh breakout). |
| RSI short threshold | < 45 | Mirror of the long threshold. |
| Exit | Opposite Donchian breakout | Per spec: exit long on a close below the prior 20-bar low, exit short on a close above the prior 20-bar high. No RSI condition on exits. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 30 | Donchian needs 20 prior bars; 30 gives margin (RSI needs 14). |

## What the exits actually did

Only 15 of 641 trades (2.3%) ended on the opposite-Donchian signal
exit; 626 ended on the harness stop/trail/max-hold. The 2xATR stop is
far closer than the opposite 20-bar extreme on 1h bars, so the
channel exit is effectively unreachable in practice — the shipped
system is a Donchian entry plus the harness stop/trail.

## Spec ambiguities

1. **RSI threshold 55/45 vs the source's 30/70.** The linked source
   is a mean-reversion variant (touch the band, RSI exits 30/70).
   The spec as written defines the breakout variant with RSI > 55 /
   < 45 as the confirmation, and that is what ships. The 30/70
   touch-and-reverse version is a different system and was not built.
2. **RSI as a level check, not a cross.** The spec says "AND RSI(14)
   > 55" — a level condition on the breakout bar, not a cross. The
   shipped version checks the level on the breakout bar.
3. **Breakout is a strict close beyond the channel.** A close exactly
   on the prior 20-bar high/low is not a breakout (strict > / <).

No bug fixes requiring re-runs, no PnL-selected tuning.
