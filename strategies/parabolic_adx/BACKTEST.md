# Parabolic ADX — Backtest

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
| BTC | 91 | 28.6% | -1662.53 | -1.77 | -21.8% | -18.27 | 0.63 |
| ETH | 82 | 34.1% | -673.76 | -0.78 | -12.5% | -8.22 | 0.79 |
| HYPE | 88 | 28.4% | -1422.30 | -1.89 | -15.5% | -16.16 | 0.64 |
| **Combined** | **261** | **30.3%** | **-3758.58** | **-2.25** | **-15.1%** | **-14.40** | **0.68** |

Fees: total $1837.59.
Exits: BTC {'stop': 62, 'signal': 29}; ETH {'stop': 59, 'signal': 23}; HYPE {'stop': 54, 'signal': 34}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$26241.42.

## Verdict: LOSER — -$3,758.58 on 261 trades, combined Sharpe -2.25, MaxDD -15.1%.

PSAR flips gated by ADX lose on 1h crypto: 261 trades, a 30.3%
win rate, PF 0.68, and -$3,758.58 net after $1,837.59 in fees.
No coin wins — HYPE is the worst by Sharpe (-1.89, -$1,422.30),
BTC loses -$1,662.53 and ETH -$673.76. The ADX > 25 gate cuts
the trade count to roughly a quarter of the ungated PSAR
strategy, but the trades it keeps are no better: the exit split
(175 stop vs 86 signal) shows most trades still reverse into
the 2xATR stop before the opposite flip or the ADX < 20 exit
fires, and the per-trade expectancy (-$14.40) is the worst of
this batch. ADX strength does not rescue a lagging flip signal.
No parameter was tuned; the spec shipped as written and lost.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 261 trades across three coins, all losing with PF 0.63–0.79
  — the edge is absent, not merely unlucky.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
