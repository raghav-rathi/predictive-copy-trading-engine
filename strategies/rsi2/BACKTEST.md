# RSI(2) Mean Reversion (Connors) — Backtest

**Data:** Hyperliquid 1h, BTC + ETH, 2026-03-14 → 2026-10-09 (~5,000 bars).
**Costs:** 0.045% taker + 0.01% slippage per side. Funding unmodeled.
**Sizing:** 1% risk on 2xATR stop, 2xATR target, 48-bar max hold, $10k start.

| Coin | Trades | Win% | Net | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 233 | 57.5% | -$1,521 (-15.2%) | -2.06 | -16.5% | -$6.32 | 0.75 |
| ETH | 220 | 55.0% | -$1,461 (-14.6%) | -1.98 | -19.0% | -$6.51 | 0.74 |
| **Combined** | **453** | — | **-$2,905** | — | — | — | — |

## Direction split (robustness check)

| Config | BTC net | ETH net |
|---|---|---|
| both sides | -15.2% | -14.6% |
| long-only | -7.4% | -6.8% |
| short-only | -8.5% | -8.4% |

Loses on both sides, both coins. The 57% win rate is the trap: winners are
small snap-backs, losers are pullbacks that keep pulling back (2xATR stop
is wide relative to the 2xATR target, and the 48-bar cap exits stale
positions at a loss).

## Verdict: LOSER in this regime

Connors' RSI(2) was designed for equity indices in structural uptrends.
On 2026 crypto 1h — choppy with sharp down-legs — buying every RSI(2) < 10
print is catching falling knives faster than the snap-backs pay. The
SMA200 trend filter did not save it. Possible future work: much tighter
entry (RSI(2) < 5), higher timeframes, or regime-gating to confirmed
uptrends only. Not for capital as a standalone.
