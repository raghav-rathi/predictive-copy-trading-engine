# Hull MA Crossover — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793887200000] (2026-03-14 22:00 UTC →
2026-11-05 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5656, ETH 5656, HYPE 5654.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 449 | 34.0% | -3928.20 | -2.42 | -43.4% | -8.75 | 0.76 |
| ETH | 423 | 37.0% | -2514.16 | -1.37 | -37.2% | -5.94 | 0.84 |
| HYPE | 416 | 37.0% | 1059.55 | 0.71 | -16.5% | 2.55 | 1.06 |
| **Combined** | **1288** | **35.9%** | **-5382.81** | **-1.42** | **-25.2%** | **-4.18** | — |

Fees: total $9423.11.
Exits: {'stop': 748, 'signal': 540}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser overall despite one green coin (HYPE +$1,059.55, PF 1.06). BTC/ETH both lose with PF 0.76/0.84; the crossover whipsaws in range-bound chop and the 2xATR stop fires more often than the opposite cross (748 stops vs 540 signal exits). Hull's own warning holds up — the crossover variant reintroduces the lag/whipsaw the HMA was meant to remove.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
