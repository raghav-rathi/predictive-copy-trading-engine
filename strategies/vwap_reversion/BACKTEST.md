# Anchored VWAP Reversion — Backtest

**Data:** Hyperliquid 1h, BTC + ETH, 2026-03-14 → 2026-10-09 (~5,000 bars).
**Costs:** 0.045% taker + 0.01% slippage per side. Funding unmodeled.
**Sizing:** 1% risk on 1.5xATR stop, 24-bar max hold, $10k start.

| Coin | Trades | Win% | Net | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 310 | 41.0% | -$6,411 (-64.1%) | -5.64 | -65.5% | -$20.68 | 0.52 |
| ETH | 285 | 47.0% | -$3,998 (-40.0%) | -2.68 | -41.3% | -$14.03 | 0.73 |
| **Combined** | **595** | — | **-$10,409** | — | — | — | — |

Threshold scan (z-entry): z=2.5 → BTC -17.6% / ETH -1.3%; z=3.5 →
BTC -6.3% / ETH +1.3% (17 trades, noise). Wider entries bleed less but
never turn positive.

## Verdict: LOSER, worst in the library

Fading 1.5-ATR stretches from daily VWAP on 1h crypto is fighting the
market's intraday trend structure: in a trending regime price stays
stretched all day and the 1.5xATR stop gets run over 595 times. VWAP
reversion is an equities-market-making edge (mean-reverting intraday
order flow); crypto perps trend intraday and it does not transfer.
Killed — no further calibration warranted.
