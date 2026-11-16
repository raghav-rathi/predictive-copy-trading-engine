# DeMark Pivots — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-11-16 14:00 UTC
(ms `[1773525600000, 1794837600000)`): 5,920 bars BTC/ETH, 5,918 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap,
$10k start. WARMUP=48 bars.

## Results (shipped config: DeMark pivots from the prior 24-bar "day",
long on a close breaking above R1 and holding 2 bars, short mirrored,
exit on a close back inside the band or the opposite level touched,
~1.5xATR stop, ~3xATR target, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 468 | 30.8% | -$5,776 | -57.8% | -7.31 | -59.2% | -$12.34 | 0.43 | $4,501 |
| ETH | 459 | 36.8% | -$4,354 | -43.5% | -4.88 | -47.7% | -$9.49 | 0.59 | $3,835 |
| HYPE | 493 | 45.8% | -$2,535 | -25.3% | -2.39 | -28.1% | -$5.14 | 0.77 | $2,926 |
| **Combined** | **1,420** | **38.0%** | **-$12,665** | — | — | — | **-$8.92** | — | **$11,262** |

Signal gates fire constantly (long entries 250/243/248, short entries
221/219/249 for BTC/ETH/HYPE). BTC is the worst leg of the whole
batch: -57.8% with Sharpe -7.31, profit factor 0.43 and a -59.2% max
drawdown — the rolling 24-bar "day" recomputes its levels every hour,
so yesterday's R1 is today's noise and breakouts are just momentum
chasing on a 1-hour clock.

## Verdict: worst strategy of the batch

Combined -$12,665 across 1,420 trades — the largest dollar loss of
the four batch-37 strategies, and the only one with a coin below
-50%. A daily pivot recomputed hourly is not a daily pivot: the
levels have no memory, no auction behind them, and the 2-bar hold
confirms breakouts that are already exhausted. HYPE's 45.8% win rate
is the best of the batch's legs and still loses -$2,535.

## Calibration note

Shipped the specified 24-bar "day". A 12 – 24 – 48 sweep is in
CALIBRATION.md: every setting loses on every coin, and the shipped
24-bar day is the least bad combined (-$12,665 vs -$14,360 /
-$14,858). The 24-bar day was fixed a priori — adopted before the
sweep, not because of it.

## Mechanism

From the prior 24-bar "day" OHLC: X = H+2L+C if C<O, 2H+L+C if
C>O, H+L+2C if C=O; R1 = X/2 − L, S1 = X/2 − H. Long on a close
breaking above R1 and holding 2 bars; short mirrored. Exit on a
close back inside the R1/S1 band or the opposite level touched.
Stop ~1.5xATR (≈ beyond the opposite level + 0.5xATR), target
~3xATR (≈ 1.5x daily range) — both are ATR approximations of
level-based rules, documented in risk.py. 24-bar max hold.

Source: DeMark Pivot Points (Tom DeMark) —
https://www.babypips.com/learn/forex/other-pivot-point-calculation-methods

## Limitations

- Only one S/R level each side, and the "day" rolls every hour —
  the levels carry none of the auction memory a real daily pivot
  has. That is the design as specified, and the backtest says it
  does not work on 1h crypto.
- Stop/target are ATR approximations of level-based rules, not the
  exact DeMark levels (see risk.py).
- 1,420 trades at ~$7.93/trade in fees; single 8-month window;
  funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped day length on this window (see CALIBRATION.md).
