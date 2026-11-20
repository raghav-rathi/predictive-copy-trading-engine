# EMA Cross + Session VWAP Momentum — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is. The sweep
below was run after the fact for reporting only; no alternate was
adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| EMA fast / slow | 9 / 21 | The canonical short-term EMA crossover pair. |
| Session VWAP | UTC-day anchored, reset 00:00 UTC, tp = (h+l+c)/3 | The standard session VWAP definition; the UTC day is the natural session for 24/7 crypto. |
| Entry | EMA cross AND close on the VWAP-agreeing side on the same bar | The spec's cross + VWAP filter: the cross alone is not enough, price must already be on the right side of the day's VWAP. |
| Exit | EMA cross against OR close back through the VWAP against the position | The spec's exit: either the trend leg or the value leg breaking ends the trade. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | EMA(21) needs 21 bars and the VWAP needs a day of bars to be meaningful; 60 gives margin. |

## Sweep (2 alternates, run and reported honestly)

Window and risk layer identical to the shipped run; only the EMA
pair changes.

| Setting | Trades | Win% | Net $ | PF | Fees $ |
|---|---|---|---|---|---|
| Shipped EMA(9,21) | 799 | 30.3% | -5589.78 | 0.79 | 6152.82 |
| Alt A EMA(5,13) | 1343 | 27.9% | -8732.00 | 0.78 | 9345.12 |
| Alt B EMA(21,50) | 328 | 35.7% | -1603.60 | 0.87 | 2715.42 |

Per-coin net for Alt A: BTC -4591, ETH -3869, HYPE -272. For Alt B:
BTC -702, ETH -1423, HYPE +522. The faster pair trades far more
(1343 trades) and loses more; the slower pair trades far less (328)
and loses least, but still ends negative on BTC and ETH with PF
0.87 combined. Fewer, slower trades lose less — consistent with
the signal being mostly noise — but no setting turns green.
Shipped config stands as specified.

## Spec decisions / ambiguities

1. **VWAP exit is a level, not a cross.** The exit fires on any
   bar where the close is on the wrong side of the session VWAP
   (close < VWAP for a long), not only on the bar the close
   crosses through it. This makes the VWAP a tight leash: a long
   entered while price is above VWAP exits on the first close
   below VWAP, even if that close is only marginally below. The
   shipped run's exit mix (489 signal exits vs 310 stops) shows
   this leash doing most of the exiting.
2. **VWAP uses the current day's bars only.** The anchored VWAP
   resets at 00:00 UTC; a trade held across midnight gets its
   exit reference from the new day's VWAP, which starts at the
   first bar's typical price and is therefore very close to price
   early in the day.
3. **Entry requires the cross and the VWAP side on the same bar.**
   A cross that happens while price is on the wrong side of VWAP
   produces no entry, even if price moves to the right side on
   the next bar without a fresh cross.
4. **EMA cross is `crossed_above/below` from `strategies.base`.**
   A cross requires the fast EMA to move from ≤ to > the slow EMA
   (strictly greater on the cross bar); equal EMAs do not cross.

## What the exits actually did

Shipped run (799 trades): 489 trades ended on a signal exit (EMA
cross against or close back through VWAP) and 310 on the harness
stop / trail. Signal exits dominate on all three coins — the
VWAP leash and the EMA cross-against exit cut trades short, which
is why the win rate is only 30.3% with PF 0.79: winners are exited
early while the 2xATR stops still take full losses.

No bug fixes requiring re-runs, no PnL-selected tuning.
