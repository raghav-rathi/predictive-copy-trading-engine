# Turtle Trading — Backtest

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
| BTC | 215 | 33.0% | -2252.74 | -1.51 | -26.2% | -10.48 | 0.77 |
| ETH | 198 | 34.0% | 190.62 | 0.25 | -19.7% | 0.96 | 1.02 |
| HYPE | 220 | 33.0% | -1006.91 | -0.54 | -21.0% | -4.58 | 0.91 |
| **Combined** | **633** | **33.6%** | **-3069.02** | **-0.91** | **-15.3%** | **-4.85** | — |

Fees: total $4906.18.
Exits: {'stop': 563, 'signal': 70}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 633 trades, -$3,069.02, PF 0.89. ETH's +$190.62 (PF 1.02) is breakeven noise, not a win; BTC and HYPE both lose. The Turtle breakout system repeats the batch's channel-breakout failure mode — 89% of exits are stops.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
