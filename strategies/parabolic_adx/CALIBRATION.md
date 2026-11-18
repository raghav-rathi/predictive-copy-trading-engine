# Parabolic ADX — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| PSAR step / max AF | 0.02 / 0.20 | Wilder's standard PSAR parameters, per the spec. |
| ADX period | 14 | Wilder's standard ADX period, per the spec. |
| ADX entry threshold / exit threshold | > 25 / < 20 | The spec's thresholds: 25 is the conventional "trending" line, 20 the "trend exhausted" line. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | ADX(14) needs ~28 bars to seed (two Wilder smoothings); 60 gives margin. |

## Spec decisions / ambiguities

1. **A PSAR flip is a strict side change between bars.**
   `psar < c AND psar.shift(1) > c.shift(1)` — the SAR must
   have been strictly above the prior close and be strictly
   below the current close. Equality on either bar is not a
   flip. This uses only the SAR/close values through bar i.
2. **ADX thresholds are strict.** ADX exactly 25 does not enter;
   ADX exactly 20 does not exit. DI comparison is also strict
   (equal DIs confirm neither side).
3. **The ADX < 20 exit can fire while ADX was never > 25.**
   A trade entered at ADX > 25 can exit the same way, but a
   trade entered long could also exit on ADX < 20 even if the
   PSAR never flips — that is the spec's "trend exhausted" exit,
   applied as written.
4. **PSAR initialisation.** Same seed as the sibling strategy:
   long with SAR = low[0], EP = high[0] (bar 0 only, no
   lookahead). The PSAR flips within one bar on a falling open.
5. **Harness stop/trail as an additional exit.** The spec's exits
   are the opposite PSAR flip / ADX < 20; the batch-standard
   risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is
   applied on top, per the batch instruction.

## What the exits actually did

Shipped run (261 trades): 175 trades ended on the harness
stop/trail and 86 on a signal exit (BTC 62 stop / 29 signal,
ETH 59 / 23, HYPE 54 / 34). The ADX < 20 exit rarely gets a
chance to fire first — most trades hit the 2xATR stop while
ADX is still above 20, which is consistent with PSAR flips on
1h crypto being whipsaws even inside a nominally strong trend.

No bug fixes requiring re-runs, no PnL-selected tuning.
