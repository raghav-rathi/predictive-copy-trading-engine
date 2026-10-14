# Williams Volatility Breakout — Backtest

**Data:** Hyperliquid 1h, BTC + ETH, 2026-03-14 → 2026-10-09 (~5,000 bars).
**Costs:** 0.045% taker + 0.01% slippage per side. Funding unmodeled.
**Sizing:** 1% risk on 1.5xATR stop, 2xATR target, 48-bar max hold, $10k start.
**Source:** https://www.investopedia.com/articles/trading/02/081402.asp

| Coin | Trades | Win% | Net | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 77 | 49.4% | +$730 (+7.3%) | 0.83 | -9.7% | +$9.48 | 1.16 |
| ETH | 80 | 45.0% | +$80 (+0.8%) | 0.17 | -12.5% | +$1.01 | 1.02 |
| **Combined** | **157** | — | **+$810 (+4.0%)** | — | — | — | — |

## Verdict: SMALL POSITIVE

Positive on both coins — the range-expansion filter is doing real work:
requiring the 24h range to exceed 1.5x its average keeps it out of dead
markets where plain breakouts (Donchian-20, Keltner) get chopped. But the
edge is thin (profit factor 1.16/1.02) and ETH is barely breakeven. The
49% win rate with a 2:1 target/stop is the right shape; it just needs more
markets and a longer window to prove it's not luck. Ensemble-sleeve
candidate alongside the squeeze — not for capital as a standalone.
