# Bull Bear Power — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794488400000) (2026-03-14 22:00 UTC →
2026-11-12 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5823, ETH 5823, HYPE 5821.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 1198 | 27.6% | -8663.75 | -9.18 | -86.7% | -7.23 | 0.49 |
| ETH | 1259 | 31.3% | -8074.71 | -7.93 | -81.3% | -6.41 | 0.58 |
| HYPE | 1156 | 35.2% | -5972.00 | -4.23 | -60.2% | -5.17 | 0.71 |
| **Combined** | **3613** | **31.3%** | **-22710.46** | **-9.69** | **-75.8%** | **-6.29** | **0.60** |

Fees: total $15667.13.
Exits: BTC {'signal': 892, 'stop': 306}; ETH {'signal': 954, 'stop': 305}; HYPE {'signal': 888, 'stop': 268}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$7,274.26.

## Verdict: LOSER — -$22,710.46 on 3,613 trades, combined Sharpe -9.69, MaxDD -75.8%.

The worst batch-34 result by a wide margin, and the failure mode is
structural: Elder's turn conditions fire on almost every bar. Bear
Power "rising vs the prior bar" and Bull Power "falling vs the prior
bar" are one-bar jitters, not turns — on hourly bars the powers flip
direction constantly, so the system takes 3,613 trades in ~5,823 bars
(roughly one trade every five bars per coin) and exits 2,734 of them
on the opposite turn within a bar or two. The churn burns $15,667.13
in fees alone, and the combined equity curve falls 75.8% from peak,
ending at $7,274.26 on a $30,000 start. No coin is close to breakeven
(best PF 0.71 on HYPE). Elder designed the Elder-Ray as a
confirmation tool inside the Triple Screen, with the EMA(13) slope as
the trend filter — traded standalone on bar-to-bar turns, the signal
is noise. The spec as written was implemented faithfully and the
result is what it is: do not trade this as specified.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 3,613-trade sample: the loss is not a small-sample fluke — the
  system over-trades by construction.
- The result is the turn conditions + harness stop/trail as
  specified; adding Elder's EMA-slope trend filter would be a
  different system, not a tuning of this one.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
