# QQE — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-15
(BTC 5,152 bars; ETH 5,152; HYPE 5,150).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: smoothed RSI(14) + fast/slow volatility
trailing levels, Fast-TL/Slow-TL cross entries, opposite-cross exits,
1.5xATR stop, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 301 | 37.5% | −$4,111 | −40.4% | −2.46 | −44.9% | −$13.66 | 0.73 |
| ETH | 345 | 35.9% | −$3,728 | −36.9% | −1.95 | −42.8% | −$10.81 | 0.77 |
| HYPE | 327 | 45.6% | +$5,922 | +61.8% | +2.48 | −17.9% | +$18.11 | 1.29 |
| **Combined** | **973** | **39.7%** | **−$1,917** | — | — | — | **−$1.97** | — |

## Verdict: HYPE star (+61.8%, Sharpe 2.48), majors losers

The batch's best single-coin result: QQE's volatility trailing levels
kept the system in HYPE's 2026 trend legs at a 45.6% win rate with a
1.29 profit factor. BTC/ETH chop kills it (−40%/−37%) — the trailing
bands are sticky in the wrong way when there is no trend to trail.
Combined −$1,917 hides a coin-scoped winner. The factor sweep (3.0 and
6.0) both underperform the shipped 4.236, so the classic Glaz setting
stands. HYPE-only sleeve candidate pending walk-forward validation.
