# Elder Force Index pullback — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars,
2026-03-14 22:00 UTC → 2026-10-10 13:00 UTC (BTC/ETH 5037 bars, HYPE 5035 bars).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(short holds dominate; noted as a limitation).
**Sizing:** 1% equity risk per trade on the 2.5xATR(14) stop, 3x leverage cap, $10k start.
Warmup 48 bars.

## Results (shipped config: FI13 trend / FI2 trigger, 2.5xATR stop, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 844 | 38.0% | -$5,870.56 | -58.7% | -8.19 | -59.6% | -$6.96 | 0.53 |
| ETH | 828 | 41.9% | -$4,552.42 | -45.5% | -4.90 | -48.3% | -$5.50 | 0.66 |
| HYPE | 861 | 47.0% | -$1,478.24 | -14.8% | -1.56 | -22.3% | -$1.72 | 0.89 |
| **Combined** | **2,533** | **42.3%** | **-$11,901.22** | — | — | — | **-$4.70** | — |

## Verdict: LOSER — negative on all three coins

The 2-period trigger EMA crosses zero constantly in 1h chop: 2,533 trades
across three coins, ~$3.4k of the loss is pure fee/slippage drag, and the
win rate never clears the payoff math (profit factor 0.53–0.89). The FI2
hook exit cuts winners the moment fast force peaks, while the 2.5xATR stop
absorbs full pullbacks that keep extending — in the March–October 2026
window the "dip into an uptrend" mostly bought the start of a breakdown.
HYPE loses the least (profit factor 0.89) but is still red.

## Volume caveat

Hyperliquid perp volume is exchange-reported, not independently auditable;
max/median hourly volume ratios are 29x (BTC), 34x (ETH), 38x (HYPE), and
no zero-volume bars exist. Any wash/incentivized volume distorts FI
directly, since FI = Δclose × volume. The test fixture exposed the flip
side: a single high-volume dip bar can drag FI13 negative by itself,
erasing the "trend" the entry depends on.

## Mechanism

FI = (close − prev close) × volume; FI13 = EMA(FI,13) is the trend,
FI2 = EMA(FI,2) the trigger. Long when FI13 > 0 and FI2 crosses below 0;
short when FI13 < 0 and FI2 crosses above 0. Exit on FI13 sign flip or a
1-bar FI2 hook against the position (peak above zero while long, trough
below zero while short). 2.5xATR(14) hard stop, no trailing, no target,
168-bar max hold. Entries execute at the next bar's open per the harness
convention.
