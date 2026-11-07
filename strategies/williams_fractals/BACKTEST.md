# Williams Fractal Breakout — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1794060000000] (2026-03-14 22:00 UTC →
2026-11-07 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5704, ETH 5704, HYPE 5702.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 186 | 32.8% | -967.31 | -0.56 | -18.5% | -5.20 | 0.88 |
| ETH | 205 | 25.9% | -2138.32 | -1.48 | -27.3% | -10.43 | 0.76 |
| HYPE | 191 | 30.4% | -2046.94 | -1.64 | -30.1% | -10.72 | 0.77 |
| **Combined** | **582** | **29.6%** | **-5152.57** | **-1.69** | **-19.3%** | **-8.85** | **0.80** |

Fees: total $4378.04.
Exits: {'stop': 479, 'signal': 103}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 582 trades, -$5,152.57, PF 0.80 — the
worst of this batch. Fractal levels on 1h crypto are routinely
re-tested and broken back through: 82% of exits are the 2xATR stop,
and the Alligator filter does not save the entries — every coin is
red (BTC -$967.31, ETH -$2,138.32, HYPE -$2,046.94). Win rate 29.6%
with expectancy -$8.85/trade — no edge here, reported as-is.

## Limitations

- Single ~7.7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
