# Raschke 3-Bar Triangle — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795010400000) (2026-03-14 22:00 UTC →
2026-11-18 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5968, ETH 5968, HYPE 5966.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 397 | 30.5% | -5204.81 | -3.57 | -58.1% | -13.11 | 0.63 |
| ETH | 403 | 31.5% | -3401.56 | -1.79 | -43.7% | -8.44 | 0.76 |
| HYPE | 334 | 38.6% | -1618.89 | -0.84 | -20.2% | -4.85 | 0.88 |
| **Combined** | **1134** | **33.2%** | **-10225.27** | **-2.64** | **-38.3%** | **-9.02** | **0.76** |

Fees: total $7373.98.
Exits: BTC {'stop': 271, 'signal': 126}; ETH {'stop': 280, 'signal': 123}; HYPE {'stop': 216, 'signal': 118}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$19,735.40.

## Verdict: LOSER — -$10,225.27 on 1,134 trades, combined Sharpe -2.64, MaxDD -38.3%.

The 3-bar triangle is the worst batch-39 strategy by dollars and
by drawdown: 1,134 trades, a 33.2% win rate, PF 0.76, and
-$10,225.27 net after $7,373.98 in fees. Every coin loses badly
— BTC -$5,204.81 (Sharpe -3.57, MaxDD -58.1%), ETH -$3,401.56
(MaxDD -43.7%), HYPE -$1,618.89 (the least bad, PF 0.88). The
sample is large, so this is not noise: inside-bar contractions
are so frequent on 1h crypto that the "triangle" fires constantly,
and the 1.25x volume filter does not separate real range
expansions from ordinary volatility — most breakouts reverse
into the 2xATR stop (767 stop vs 367 signal exits). No parameter
was tuned; the spec shipped as written and lost heavily.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 1,134 trades is a large sample and the loss is present on all
  three coins — the edge is absent, not merely unlucky.
- Contractions cluster, so the "new contraction restarts the
  triangle" choice (see CALIBRATION.md) matters; keeping the
  first triangle instead would trade a different set of breaks.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
