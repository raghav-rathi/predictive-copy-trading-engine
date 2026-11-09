# Gann Square of Nine — Backtest

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
| BTC | 2065 | 37.3% | -9489.69 | -17.57 | -95.1% | -4.60 | 0.42 |
| ETH | 755 | 32.5% | -4657.40 | -3.89 | -47.3% | -6.17 | 0.74 |
| HYPE | 207 | 20.8% | -2046.26 | -2.23 | -26.8% | -9.89 | 0.70 |
| **Combined** | **3027** | **35.0%** | **-16193.35** | **-9.19** | **-54.8%** | **-5.35** | **0.60** |

Fees: total $12190.82.
Exits: {'signal': 2678, 'stop': 348, 'max_hold': 1}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser — catastrophic on paper (−$16,193.35 combined, PF 0.60).

The 45° ladder is far too dense on high-priced coins to trade as a breakout system: on BTC the levels sit ~0.18% apart, so the strategy fires 2,065 trades (roughly every third bar), and most exits are the close falling back below the entry level one bar later — a 0.18% target against 0.11% round-trip fees leaves nothing after costs, and the 37.3% win rate cannot carry it. BTC equity fell 95.1% peak-to-trough. ETH (755 trades) and HYPE (207 trades, where the 0.5% filter usually blocks entry) lose as well. The Square of Nine levels are geometry, not a signal: price crosses them constantly and respects them rarely. Do not trade.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
