# Bollinger + RSI Mean Reversion — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1792328400000) (2026-03-14 22:00 UTC →
2026-10-18 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5223, ETH 5223, HYPE 5221.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 198 | 57.6% | -1540.92 | -1.70 | -15.4% | -7.78 | 0.78 |
| ETH | 173 | 53.2% | -2209.17 | -2.78 | -24.0% | -12.77 | 0.67 |
| HYPE | 210 | 52.9% | -2380.27 | -2.92 | -26.8% | -11.33 | 0.70 |
| **Combined** | **581** | **54.6%** | **-6130.37** | **-3.55** | **-20.8%** | **-10.55** | **0.71** |

Fees: total $4507.84.
Exits: {'signal': 343, 'stop': 238}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 581 trades, −$6130.37, PF 0.71 — the
worst of this batch, and red on all three coins. The paradox is
instructive: win rate is above 50% everywhere (53–58%), yet every coin
loses money, so average losers dwarf average winners. Catching the
recovery close after an RSI(2) < 10 washout on 1h crypto means buying
into moves that keep falling — the 2xATR stop then takes a full-size
loss while winners are capped by the exit at the middle band. A
clean, consistent rejection of this mean-reversion setup on 1h crypto.

## Limitations

- Single ~7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
