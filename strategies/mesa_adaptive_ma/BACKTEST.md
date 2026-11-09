# MESA Adaptive Moving Average Crossover — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794232800000) (2026-03-14 22:00 UTC →
2026-11-09 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5752, ETH 5752, HYPE 5750.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 230 | 32.6% | -2150.82 | -1.41 | -26.6% | -9.35 | 0.77 |
| ETH | 266 | 33.8% | 376.66 | 0.34 | -22.5% | 1.42 | 1.03 |
| HYPE | 205 | 38.0% | 981.29 | 0.74 | -15.1% | 4.79 | 1.11 |
| **Combined** | **701** | **34.7%** | **-792.87** | **-0.14** | **-15.0%** | **-1.13** | **0.97** |

Fees: total $6062.56.
Exits: BTC {'stop': 181, 'signal': 49}; ETH {'stop': 206, 'signal': 60}; HYPE {'stop': 174, 'signal': 31}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined on paper (−$792.87, PF 0.97, Sharpe −0.14).

MAMA/FAMA fires far too often on 1h crypto — 701 trades in ~8 months — and most of them die on the ATR stop (561 of 701 exits are stops, only 140 are signal exits). The adaptive alpha does not buy whipsaw immunity here: BTC loses −$2,150.82 with a −26.6% drawdown, and the ETH/HYPE gains (+$376.66 / +$981.29) do not cover it. Win rate 34.7% with PF 0.97 is a breakeven-to-losing system before fees; after $6,062.56 of fees it is clearly negative. Not a tradeable signal as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
