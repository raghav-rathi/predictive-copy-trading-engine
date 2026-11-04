# Outside Bar Breakout — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793800800000] (2026-03-14 22:00 UTC →
2026-11-04 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5633, ETH 5633, HYPE 5631.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 162 | 25.3% | -3477.52 | -4.17 | -36.8% | -21.47 | 0.47 |
| ETH | 112 | 29.5% | -359.51 | -0.34 | -15.1% | -3.21 | 0.92 |
| HYPE | 153 | 36.6% | 2261.94 | 1.91 | -8.5% | 14.78 | 1.34 |
| **Combined** | **427** | **30.4%** | **-1575.09** | **-0.80** | **-10.1%** | **-3.69** | — |

Fees: total $3391.90.
Exits: {'stop': 270, 'signal': 157}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined despite HYPE +$2,262 (Sharpe 1.91): BTC -$3,478 drags it negative. Outside-bar breaks work on trending HYPE, fail in BTC chop.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
