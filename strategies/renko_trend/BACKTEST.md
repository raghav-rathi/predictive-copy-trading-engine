# Renko Trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-15
(BTC 5,152 bars; ETH 5,152; HYPE 5,150).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: 0.5xATR renko bricks from closes,
brick-reversal entries, opposite-reversal exits, 2xATR stop, 200-bar
max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 860 | 26.9% | −$7,864 | −78.5% | −7.44 | −79.2% | −$9.14 | 0.58 |
| ETH | 800 | 31.6% | −$5,602 | −55.9% | −3.59 | −60.9% | −$7.00 | 0.70 |
| HYPE | 911 | 33.6% | −$6,196 | −61.8% | −4.90 | −63.6% | −$6.80 | 0.71 |
| **Combined** | **2,571** | **30.7%** | **−$19,662** | — | — | — | **−$7.65** | — |

## Verdict: worst in batch — brick reversals on 1h are pure churn

Renko's noise filtering assumes the noise is smaller than the brick;
on 1h crypto the noise IS the brick size, so every wiggle prints a
reversal: 2,571 trades, Sharpe −7.44 on BTC. The 0.25xATR variant is
even worse (−$25,397, 4,491 trades); the 1.0xATR variant loses less
(−$5,786) but stays negative everywhere including HYPE. Bigger bricks
just mean slower bleeding. The concept needs trending daily+ structure
to work; on 1h perps it is a fee-donation machine. Killed.
