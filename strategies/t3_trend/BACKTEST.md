# Tillson T3 — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-15
(BTC 5,152 bars; ETH 5,152; HYPE 5,150).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: T3(5)/T3(15) cross, a=0.7, opposite-cross
exits, 2xATR stop, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 295 | 32.2% | −$1,490 | −11.6% | −0.41 | −30.0% | −$5.05 | 0.90 |
| ETH | 317 | 30.0% | −$2,737 | −24.0% | −1.12 | −38.4% | −$8.64 | 0.81 |
| HYPE | 289 | 39.1% | +$2,926 | +30.3% | +1.54 | −19.2% | +$10.13 | 1.18 |
| **Combined** | **901** | **33.6%** | **−$1,301** | — | — | — | **−$1.44** | — |

## Verdict: mixed — HYPE winner, majors losers

The low-lag smoother does what it promises on HYPE (+30.3%, Sharpe
1.54, 39.1% win rate) and fails on BTC/ETH chop. Combined −$1,301 is
near breakeven, which flatters a system that is really two different
systems by coin. The slower T3(8,21) variant is the interesting one
(combined −$821, BTC Sharpe +0.23, HYPE +0.58) — less bad everywhere —
while the fast T3(3,8) is a churn machine (−$13,126, 1,708 trades).
Regime-dependent; research material only.
