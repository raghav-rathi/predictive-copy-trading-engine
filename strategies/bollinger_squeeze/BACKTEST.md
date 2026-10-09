# Bollinger Squeeze Expansion — Backtest

**Data:** Hyperliquid 1h, BTC + ETH, 2026-03-14 → 2026-10-09 (~5,000 bars).
**Costs:** 0.045% taker + 0.01% slippage per side. Funding unmodeled.
**Sizing:** 1% risk on 1.5xATR stop, 3xATR target, 72-bar max hold, $10k start.

| Coin | Trades | Win% | Net | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 120 | 40.0% | +$318 (+3.2%) | 0.36 | -16.6% | +$2.65 | 1.04 |
| ETH | 125 | 39.2% | +$303 (+3.0%) | 0.35 | -13.3% | +$2.42 | 1.04 |
| **Combined** | **245** | — | **+$621 (+3.1%)** | — | — | — | — |

## Verdict: SMALL POSITIVE, fragile

Positive on both coins with 245 trades — the most consistent result so far.
But the profit factor (1.04) is razor-thin and max drawdown (-16.6%) is
large relative to the +3% return: the return/DD ratio is poor. The squeeze
release does capture expansion moves, but too many releases fizzle into the
1.5xATR stop.

Possible improvements: require a minimum squeeze duration (coiled longer =
bigger move), add a volume-expansion confirm on the release bar, or widen
the target. Candidate for an ensemble sleeve with a drawdown overlay — not
for capital as a standalone.
