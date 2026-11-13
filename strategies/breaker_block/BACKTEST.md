# Breaker Block — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794574800000) (2026-03-14 22:00 UTC →
2026-11-13 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5847, ETH 5847, HYPE 5845.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 56 | 33.9% | -1017.96 | -1.45 | -12.2% | -18.18 | 0.62 |
| ETH | 49 | 34.7% | 82.42 | 0.17 | -9.5% | 1.68 | 1.04 |
| HYPE | 84 | 32.1% | -565.69 | -0.58 | -12.7% | -6.73 | 0.86 |
| **Combined** | **189** | **33.3%** | **-1501.22** | **-1.02** | **-8.8%** | **-7.94** | **0.84** |

Fees: total $1510.10.
Exits: BTC {'stop': 53, 'signal': 3}; ETH {'stop': 47, 'signal': 2}; HYPE {'stop': 74, 'signal': 10}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$28,498.78.

## Verdict: LOSER — -$1,501.22 on 189 trades, combined Sharpe -1.02, MaxDD -8.8%.

The breaker block loses on BTC (-$1,017.96, PF 0.62) and HYPE
(-$565.69, PF 0.86) and is essentially flat on ETH (+$82.42,
PF 1.04). Win rate 33.3% with PF 0.84 does not clear $1,510.10 in
fees. The exit split is the honest tell: 174 of 189 trades ended
on the harness stop/trail and only 15 on the opposite breaker
signal, so the shipped system is effectively a breaker-retest
entry plus the 2xATR stop / 2.5xATR trail — and the retest entries
do not reverse hard enough, often enough, to pay for the stop.
The setup is selective (189 trades in ~8 months across three
coins), which keeps the drawdown mild (-8.8% combined), but
selectivity without edge is just fewer losing trades.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 189-trade sample: a real sample, but the ETH "win" (+$82 on 49
  trades) is noise-level — do not read it as an ETH-only edge.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
