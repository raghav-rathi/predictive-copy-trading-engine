# Support Resistance Flip — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794924000000) (2026-03-14 22:00 UTC →
2026-11-17 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5944, ETH 5944, HYPE 5942.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 429 | 20.3% | -4115.44 | -3.09 | -41.5% | -9.59 | 0.66 |
| ETH | 416 | 23.8% | -2435.19 | -1.50 | -29.7% | -5.85 | 0.80 |
| HYPE | 404 | 27.5% | -1812.54 | -1.22 | -29.6% | -4.49 | 0.86 |
| **Combined** | **1249** | **23.8%** | **-8363.17** | **-2.73** | **-28.6%** | **-6.70** | **0.77** |

Fees: total $8899.17.
Exits: BTC {'signal': 274, 'stop': 155}; ETH {'signal': 273, 'stop': 143}; HYPE {'signal': 268, 'stop': 136}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$21,665.15.

## Verdict: LOSER — -$8,363.17 on 1,249 trades, combined Sharpe -2.73, MaxDD -28.6%.

Break-and-retest loses on every coin, and it is the most active
system of the batch: 1,249 trades (vs 824–825 for the other
two), yet the lowest win rate at 23.8% combined. BTC is worst
(-$4,115.44, PF 0.66, win rate 20.3%), ETH -$2,435.19
(PF 0.80), HYPE -$1,812.54 (PF 0.86). Fees alone ($8,899.17)
exceed the net loss. The exit split is the tell: unlike the
other two strategies, most trades here end on the signal exit
(815/1,249) rather than the stop — price retests the flipped
level, holds for one bar (triggering entry at the next open),
and then closes straight back across it, exiting the trade
almost immediately at a small loss. The "hold" that looks like
confirmation on the retest bar does not persist to the next
bar's open, which is when the harness actually enters. The
2-touch qualification does not save it either: twice-touched
50-bar pivot levels on 1h crypto break and retest constantly,
so the system fires far too often (about 5 trades a day per
coin) for a pattern that is supposed to be selective.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry — and here that matters more
  than usual, because the entry depends on a one-bar hold that
  frequently fails by the next open.
- 1,249-trade sample, and the loss is broad-based (all three
  coins negative, PF 0.66–0.86) — the edge is absent, not
  one-coin driven.
- The flip-level exit fires on 815/1,249 trades, so the
  reported result is dominated by the spec's own exit, not
  the harness stop/trail — the system as written whipsaws.
- The low-based touch definition (per spec) may admit levels
  a high-based definition would reject; that is a spec
  decision, not a bug, and it is documented in CALIBRATION.md.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
