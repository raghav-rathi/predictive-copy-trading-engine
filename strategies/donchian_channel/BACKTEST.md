# Donchian Channel — Backtest

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
| BTC | 228 | 32.0% | -2426.63 | -1.68 | -26.9% | -10.64 | 0.75 |
| ETH | 205 | 34.0% | 16.56 | 0.14 | -19.4% | 0.08 | 1.00 |
| HYPE | 230 | 36.0% | -705.59 | -0.33 | -17.4% | -3.07 | 0.94 |
| **Combined** | **663** | **33.8%** | **-3115.66** | **-0.95** | **-15.2%** | **-4.70** | — |

Fees: total $5129.74.
Exits: {'stop': 524, 'signal': 139}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 663 trades, -$3,115.66, PF 0.90. ETH is flat (+$16.56, PF 1.00); BTC and HYPE both lose. The plain 20-bar Donchian breakout with a midline exit repeats the batch's channel-breakout failure mode — 79% of exits are stops.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
