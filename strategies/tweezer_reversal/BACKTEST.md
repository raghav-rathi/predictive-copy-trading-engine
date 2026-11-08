# Tweezer Reversal — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1792328400000] (2026-03-14 22:00 UTC →
2026-10-18 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5223, ETH 5223, HYPE 5221.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 141 | 22.0% | -1791.28 | -1.95 | -24.7% | -12.70 | 0.68 |
| ETH | 138 | 33.3% | 555.46 | 0.63 | -16.6% | 4.03 | 1.10 |
| HYPE | 163 | 34.4% | 237.80 | 0.31 | -13.6% | 1.46 | 1.04 |
| **Combined** | **442** | **30.1%** | **-998.02** | **-0.42** | **-8.4%** | **-2.26** | **0.94** |

Fees: total $3311.26.
Exits: {'stop': 273, 'signal': 168, 'max_hold': 1}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 442 trades, -$998.02, PF 0.94 — ETH
(+$555.46, Sharpe 0.63) and HYPE (+$237.80) are mildly green but
BTC (-$1791.28, Sharpe -1.95, MaxDD -24.7%, win rate 22.0%) drags
the book under water. The pattern fires often (670 entry signals
post-warmup across the three coins) but the 30.1% combined win rate
cannot cover fees and the 2xATR stops: 273 of 442 exits hit the
stop/trail. No tweezer edge on this window.

## Limitations

- Single ~7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
