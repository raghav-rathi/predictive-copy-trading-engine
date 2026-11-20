# Stochastic %K/%D Cross + MACD Histogram — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
A small two-alternate sweep was run after the fact and is reported
honestly below; the shipped config was NOT changed on its basis.

| Parameter | Value | A priori rationale |
|---|---|---|
| Stochastic | (14, 3, 3) | The canonical Lane stochastic: raw %K over 14 bars, %K = SMA(3) of raw %K, %D = SMA(3) of %K. |
| MACD | (12, 26, 9) | The canonical Appel MACD; histogram = line - signal. |
| Entry gate | cross out of oversold %K < 30 / overbought %K > 70, evaluated on the cross bar | The spec: the cross must happen while %K is still in the extreme zone. |
| Entry agreement | MACD histogram > 0 (long) / < 0 (short) on the cross bar | The spec: momentum must agree with the stochastic cross. |
| Exit | opposite %K/%D cross OR histogram sign flip against | The spec: either the cross reverses or momentum flips. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | Stochastic needs 14+3+3 bars, MACD 26+9; 40 gives margin. |

## Sweep (2 alternates, run after the shipped backtest)

Combined across BTC/ETH/HYPE, same window and risk layer:

| Config | Trades | Win% | Net $ | Profit factor | Fees $ |
|---|---|---|---|---|---|
| **Shipped (14,3,3) 30/70** | **97** | **34.0%** | **-1258.04** | **0.60** | **736.52** |
| Alt thresholds 20/80 | 15 | 33.3% | -285.44 | 0.49 | 108.68 |
| Alt stochastic (21,3,3) 30/70 | 202 | 29.2% | -2917.17 | 0.61 | 1495.31 |

Tighter extremes (20/80) nearly starve the strategy (15 trades)
and still lose; a slower stochastic (21,3,3) doubles the trade
count and loses more than twice as much. Neither alternate was
adopted — both lose, and picking the smaller loser on 15 trades
would be noise-chasing.

## Spec decisions / ambiguities

1. **The cross and the gates are simultaneous.** All three
   conditions (cross, %K in the extreme zone, histogram sign)
   must hold on the SAME bar. A cross one bar before the
   histogram flips does not enter — verified by unit test: a
   dip-recovery series crosses %K above %D at bar 45 with %K
   12.4 < 30 while the histogram is still negative, and no
   entry fires.
2. **%K is the smoothed %K** (SMA(3) of raw %K), and %D is the
   SMA(3) of that — the standard (14,3,3) construction, not raw
   %K vs its SMA.
3. **Histogram sign flip is a hard exit even without a cross.**
   A long exits the first bar the histogram goes negative, even
   if %K is still above %D.
4. **The cross uses the strict definition** (k > d now, k <= d
   last bar), so equal values on the prior bar still count as a
   cross.
5. **Flat-range %K is 50, not 0/100.** In a flat range the close
   sits mid-range; the tests pin %K = 50 for close == mid-range
   and %K = 100/0 for close pinned at the range high/low.

## What the exits actually did

Shipped run (97 trades): 73 trades ended on a signal exit
(opposite cross or histogram flip) and 24 on the harness stop /
trail. The strategy exits on its own terms most of the time — the
problem is entry quality, not exit discipline.

No bug fixes requiring re-runs, no PnL-selected tuning.
