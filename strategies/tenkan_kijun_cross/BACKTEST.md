# Ichimoku Tenkan/Kijun Cross — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794232800000) (2026-03-14 22:00 UTC →
2026-11-09 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5752, ETH 5752, HYPE 5750.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 277 | 35.4% | -1910.72 | -1.17 | -25.5% | -6.90 | 0.83 |
| ETH | 300 | 33.3% | -965.40 | -0.51 | -18.7% | -3.22 | 0.92 |
| HYPE | 286 | 38.8% | -228.90 | -0.03 | -20.9% | -0.80 | 0.98 |
| **Combined** | **863** | **35.8%** | **-3105.02** | **-0.84** | **-16.7%** | **-3.60** | **0.91** |

Fees: total $7172.54.
Exits: {'stop': 638, 'signal': 225}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins combined (−$3,105.02, PF 0.91, Sharpe −0.84) — but a mild one.

The bare TK cross fires 863 times and loses slowly everywhere: win
rates 33–39%, and 638 of 863 exits (74%) hit the ATR stop/trail
rather than the opposite cross, i.e. most crosses reverse into the
stop before the lines cross back. HYPE is nearly breakeven (PF 0.98,
−$228.90 on 286 trades), BTC the worst (−$1,910.72). The signal is
not a disaster, but without the textbook cloud/price location filter
(a cross above the cloud is the "strong" version) it is just
whipsaw-prone momentum on 1h crypto. Not tradeable as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
