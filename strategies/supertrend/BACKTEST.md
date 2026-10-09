# Supertrend (ADX-confirmed) — Backtest

**Data:** Hyperliquid 1h, BTC + ETH, 2026-03-14 → 2026-10-09 (~5,000 bars).
**Costs:** 0.045% taker + 0.01% slippage per side. Funding unmodeled.
**Sizing:** 1% risk on 2.5xATR stop, 3x leverage cap, $10k start.

| Coin | Trades | Win% | Net | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 75 | 26.7% | -$2,102 (-21.0%) | -3.11 | -21.6% | -$28.02 | 0.45 |
| ETH | 84 | 29.8% | -$1,322 (-13.2%) | -1.63 | -18.3% | -$15.84 | 0.69 |
| **Combined** | **159** | — | **-$3,432** | — | — | — | — |

## Parameter scan (BTC, honest)

| Params | ADX gate | Net | Sharpe |
|---|---|---|---|
| (10, 3.0) | off | -24.3% | -2.76 |
| (10, 3.0) | >20 | -21.0% | -3.11 |
| (7, 2.0) | off | -8.2% | -0.57 |
| (7, 2.0) | >20 | -3.0% | -0.20 |
| (14, 2.5) | off | -23.3% | -2.29 |
| (14, 2.5) | >20 | -11.4% | -1.28 |

Negative in every configuration. The ADX gate helps (cuts the worst chop)
but cannot rescue it.

## Verdict: LOSER in this regime

Supertrend flips lag too much on 1h crypto: by the time the band flips, the
impulse is exhausted and the stop is far away (2.5xATR), so exits bleed.
The (7, 2.0) variant is least-bad but still negative — kept the canonical
(10, 3.0) spec rather than overfit to the least-bad cell. Possible future
work: higher timeframes (4h/daily), or using the band as a trailing exit
only (no flip entries). Not for capital as a standalone.
