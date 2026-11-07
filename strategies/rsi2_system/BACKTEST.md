# RSI(2) System — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail. Window t in [1773525600000, 1794060000000]
(2026-03-14 22:00 UTC → 2026-11-07 13:00 UTC, last completed hour
bar; coordinator-verified on the fixed window, excluding the partial
14:00 UTC bar the standard runner pulls). $10k start per
coin, 1% risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee
+ 0.01% slippage per side, funding off.

**Bar counts used:** BTC 5704, ETH 5704, HYPE 5702.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 122 | 56.6% | -1821.92 | -3.08 | -18.7% | -14.93 | 0.49 |
| ETH | 123 | 48.8% | -1944.51 | -3.13 | -19.6% | -15.81 | 0.44 |
| HYPE | 132 | 56.8% | -642.29 | -1.11 | -9.3% | -4.87 | 0.78 |
| **Combined** | **377** | **54.1%** | **-4408.73** | **-3.60** | **-14.9%** | **-11.69** | **0.56** |

Fees: total $3059.36.
Exits: {'signal': 302, 'stop': 75}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser, 377 trades, -$4,408.73, PF 0.56 — a losing
mean-reversion read on 1h crypto. The win rate looks respectable
(54.1% combined, 56.6% on BTC) but the average loss dwarfs the
average win: expectancy -$11.69/trade, PF 0.56 on every coin. The
SMA(5) exit lets snap-backs run only a little while the 2xATR stop
absorbs full trend-continuation moves — RSI(2) <= 5 in a 1h uptrend
too often marks the start of a real selloff rather than a snap-back.
All three coins red; ETH worst (-$1,944.51, PF 0.44). The classic
daily-bars Connors setup does not transfer to 1h crypto as specified.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
