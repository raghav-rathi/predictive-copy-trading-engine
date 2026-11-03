# Wyckoff Sign of Strength — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793714400000] (2026-03-14 22:00 UTC →
2026-11-03 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 50 bars.

**Bar counts used:** BTC 5609, ETH 5609, HYPE 5607.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 189 | 29.1% | -2007.51 | -3.03 | -20.8% | -10.62 | 0.55 |
| ETH | 169 | 36.7% | -804.67 | -0.94 | -12.3% | -4.76 | 0.81 |
| HYPE | 218 | 30.3% | -2545.64 | -5.00 | -27.5% | -11.68 | 0.46 |
| **Combined** | **576** | **31.8%** | **-5357.82** | **-3.66** | **-18.6%** | **-9.30** | **0.60** |

Fees: total $4114.75.
Exits: 503 signal, 73 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins

Volume-confirmed range breakouts lose everywhere (PF 0.46-0.81); the 1.5x volume filter does not separate real breakouts from fakeouts at 1h — not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
