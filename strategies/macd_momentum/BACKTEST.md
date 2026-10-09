# MACD Histogram Momentum — Backtest

**Data:** Hyperliquid 1h, BTC + ETH, 2026-03-14 → 2026-10-09 (~5,000 bars).
**Costs:** 0.045% taker + 0.01% slippage per side. Funding unmodeled.
**Sizing:** 1% risk on 2xATR stop, 3xATR chandelier trailing, $10k start.

| Coin | Trades | Win% | Net | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 162 | 28.4% | -$2,464 (-24.6%) | -2.34 | -29.3% | -$15.21 | 0.66 |
| ETH | 184 | 28.8% | -$1,676 (-16.8%) | -1.28 | -23.4% | -$9.11 | 0.79 |
| **Combined** | **346** | — | **-$4,140** | — | — | — | — |

Direction split (BTC): long-only -8.3%, short-only -17.8% — loses everywhere.

## Verdict: LOSER, decisively

The worst performer so far. MACD histogram zero-crosses on 1h crypto are
whipsaw central: the histogram crosses, price is already extended, the
2xATR stop is far, and the reversal exit comes too late. 346 trades of
churn at -$12/trade expectancy. The EMA200 filter doesn't help because the
problem is timing, not direction. Not for capital; not even for an
ensemble sleeve without a full redesign (e.g., histogram *divergence*
entries instead of zero-crosses).
