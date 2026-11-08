# SMA-RSI Pullback — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1792328400000] (2026-03-14 22:00 UTC →
2026-10-18 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5223, ETH 5223, HYPE 5221.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 105 | 42.9% | -137.46 | -0.08 | -12.8% | -1.31 | 0.97 |
| ETH | 122 | 36.1% | 101.81 | 0.19 | -20.0% | 0.83 | 1.02 |
| HYPE | 102 | 30.4% | -843.21 | -0.98 | -12.6% | -8.27 | 0.82 |
| **Combined** | **329** | **36.5%** | **-878.86** | **-0.42** | **-12.0%** | **-2.67** | **0.94** |

Fees: total $2940.69.
Exits: {'stop': 216, 'signal': 113}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Near breakeven, 329 trades, -$878.86, PF 0.94 — a
small loser overall. ETH is marginally positive (+$101.81, PF
1.02) while BTC (-$137.46, PF 0.97) is flat and HYPE (-$843.21,
PF 0.82) is red. The 36.5% win rate with 2xATR stops roughly pays
for itself before fees; after fees it bleeds slowly. No tradable
edge on this window as specified — closest to breakeven of the
batch, but still not a winner.

## Limitations

- Single ~7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
