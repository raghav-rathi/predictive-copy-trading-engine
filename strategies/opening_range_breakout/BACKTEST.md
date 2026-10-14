# Opening-Range Breakout (bake-off winner port) — Backtest

**Data:** Hyperliquid 1h, BTC + ETH, 2026-03-14 → 2026-10-09 (~5,000 bars).
**Costs:** 0.045% taker + 0.01% slippage per side. Funding unmodeled.
**Sizing:** 1% risk, 20-bar intraday cap, $10k start.
**Source:** https://github.com/ibrahimshere/nq-l2-scalping/blob/HEAD/data/l2_winner_candidates.md

| Coin | Trades | Win% | Net (3:1) | Sharpe | MaxDD |
|---|---|---|---|---|---|
| BTC | 330 | 27.0% | -$6,227 (-62.3%) | -3.92 | -64.8% |
| ETH | 321 | 32.7% | -$1,989 (-19.9%) | -0.68 | -38.7% |

Stop/target scan: (2xATR/4xATR) → BTC -24.9% / ETH -12.9%;
(2xATR/6xATR) → BTC -29.2% / ETH -17.0%. Loses everywhere.

## Verdict: LOSER — edge does not port

The original's edge is tick-level: a 3-minute consolidation, 4-tick stop,
32-tick target (8:1) on NQ with level-2 confirmation. Ported to 1h crypto
bars, the "opening range" is arbitrary (crypto has no open), the 1xATR
stop is noise-bait, and 651 trades churn at -$13/trade expectancy. The
bake-off win (PF 8.0, 34 trades) is also a tiny sample on a different
market and timeframe. Killed — no further calibration.
