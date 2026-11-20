# Supertrend + MACD Agreement — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is. The sweep
below was run after the fact for reporting only; no alternate was
adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| Supertrend | period 10, multiplier 3.0, Wilder ATR | The canonical Supertrend defaults (Olivier Seban). |
| MACD | fast 12, slow 26, signal 9 | The canonical MACD defaults (Gerald Appel). |
| Entry | first bar Supertrend direction and MACD histogram agree | The spec's "transition into agreement" — a re-entry requires agreement to break and re-form. |
| Exit | Supertrend flip OR histogram sign flip against the position | The spec's exit: either leg of the agreement breaking ends the trade. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | Supertrend needs 10 bars of ATR, MACD histogram needs ~34 bars; 40 gives margin. |

## Sweep (2 alternates, run and reported honestly)

Window and risk layer identical to the shipped run; only the
Supertrend parameters change.

| Setting | Trades | Win% | Net $ | PF | Fees $ |
|---|---|---|---|---|---|
| Shipped ST(10, 3.0) | 896 | 32.3% | -4574.27 | 0.88 | 6775.74 |
| Alt A ST(7, 2.0) | 1030 | 34.5% | -353.37 | 0.99 | 8511.05 |
| Alt B ST(14, 4.0) | 808 | 34.2% | -1217.21 | 0.96 | 6364.69 |

Per-coin net for Alt A: BTC -2011, ETH +1475, HYPE +183. For Alt B:
BTC -1427, ETH -1188, HYPE +1398. Both alternates lose less than the
shipped config but neither turns green combined, and Alt A's near-zero
result (PF 0.99 on 1030 trades) is statistically indistinguishable
from breakeven — chasing it would be fitting noise. Shipped config
stands as specified.

## Spec decisions / ambiguities

1. **Supertrend seeding.** The shared `strategies.base.supertrend`
   seeds at the first bar with a valid ATR (bar 9 for period 10),
   not at bar 0, because the ATR itself is NaN before then. The
   seed direction uses only data through that bar (close vs the
   band midpoint). No peeking.
2. **Agreement is a transition, not a level.** Holding both
   conditions for many bars produces exactly one entry (the first
   bar they hold together). A second entry needs agreement to
   break (which exits any open position) and re-form.
3. **Histogram sign, not line-vs-signal, for the exit.** The exit
   uses the histogram turning against the position, which is the
   same event as the MACD line crossing its signal — the two
   wordings coincide.
4. **Both exit columns can be True on one row.** With Supertrend
   bullish and the histogram negative, `long_exit` is True and
   `short_exit` is also True (a short would exit on the bullish
   Supertrend). A position is only ever one side, so this is
   harmless; the tests assert only the relevant exit.

## What the exits actually did

Shipped run (896 trades): 545 trades ended on the harness stop /
trail and 351 on a signal exit. Stops dominate on BTC (174/297)
and ETH (200/298) — the 2xATR stop is the working exit more often
than the agreement break, which is also why the win rate is low
(32.3%) while the profit factor is 0.88: losers are stopped out at
~2xATR while winners are cut short by the histogram flip.

No bug fixes requiring re-runs, no PnL-selected tuning.
