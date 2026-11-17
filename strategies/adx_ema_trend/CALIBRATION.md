# ADX EMA Trend — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| EMA fast / slow | 20 / 50 | The spec's crossover pair; the standard swing-trading EMA pair from the sources. |
| ADX period | 14 | Wilder's standard ADX period. |
| ADX entry threshold | > 25 | The spec's "trending" threshold; the conventional ADX strong-trend line. Strictly greater (exactly 25 is not a trend). |
| ADX exit threshold | < 20 | The spec's "trend dead" threshold; the conventional ADX no-trend line. Strictly less (exactly 20 does not exit). |
| DI direction | +DI > -DI for longs, -DI > +DI for shorts | The spec's directional agreement test, evaluated on the cross bar. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | EMA(50) needs 50 bars to seed plus ADX smoothing lag; 60 gives margin. |

## Spec decisions / ambiguities

1. **ADX and DI are evaluated on the cross bar itself.** The spec
   says "ADX > 25 AND +DI > -DI at the cross" — all three
   conditions are read on the bar where the EMA cross occurs.
2. **The ADX < 20 exit fires for both sides.** A dead trend exits a
   long and a short alike; the exit does not require a cross.
3. **Harness stop/trail as an additional exit.** The spec's exits
   are the reverse cross / ADX < 20; the batch-standard risk layer
   (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on
   top, per the batch instruction.

## What the exits actually did

Shipped run (76 trades): 69 trades ended on the harness stop/trail
and only 7 on a signal exit (BTC 20 stop / 1 signal, ETH 27 / 5,
HYPE 22 / 1). The ADX < 20 / reverse-cross exit almost never gets
a chance — once in, the trade is usually stopped out first. A
second, structural point surfaced in testing: on a trend that
starts from flat, ADX is still NaN/seeding when the first EMA
cross fires, so the ADX > 25 condition at the cross can never be
met and the entry is missed entirely; entries only fire when a
trend is already established (e.g. a second cross after a dip).
That is the spec as written (all conditions on the cross bar), not
a bug, but it is why the strategy trades only 76 times in ~8
months.

No bug fixes requiring re-runs, no PnL-selected tuning.
