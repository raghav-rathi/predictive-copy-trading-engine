# Polarized Fractal Efficiency — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794315600000) (2026-03-14 22:00 UTC →
2026-11-10 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5775, ETH 5775, HYPE 5773.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 304 | 30.3% | -1415.80 | -0.82 | -27.0% | -4.66 | 0.88 |
| ETH | 388 | 28.4% | -3452.10 | -2.76 | -42.1% | -8.90 | 0.70 |
| HYPE | 521 | 31.9% | -1397.56 | -0.69 | -20.9% | -2.68 | 0.91 |
| **Combined** | **1213** | **30.3%** | **-6265.46** | **-1.88** | **-26.2%** | **-5.17** | **0.84** |

Fees: total $8539.97.
Exits: BTC {'signal': 157, 'stop': 147}; ETH {'signal': 235, 'stop': 153}; HYPE {'signal': 331, 'stop': 190}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined on paper (−$6,265.46, PF 0.84, Sharpe −1.88).

PFE fires far too often on 1h crypto — 1,213 trades in ~8 months, roughly
five a day across the three coins — and the reversal-from-extreme entries
do not pay: every coin loses, win rate is only 30.3% with PF 0.84, and ETH
is the worst of the three (−$3,452.10, −42.1% drawdown, Sharpe −2.76).
Signal exits (723) slightly outnumber stops (490), so the losses are not
mostly stop-outs — the entries themselves are usually wrong, with the
peak-reached exit giving back what little the move offered. After $8,539.97
of fees on 1,213 round trips the system is decisively negative. Not a
tradeable signal as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The EMA(5) smoothing lets PFE whipsaw across zero in chop, which is
  exactly when the reversal entries trigger most; the 20-bar extreme
  filter (±30) does not screen that out on 1h data.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
