# VWMA Crossover — Backtest

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
| BTC | 194 | 30.0% | -2735.88 | -2.28 | -32.9% | -14.10 | 0.68 |
| ETH | 198 | 34.0% | 1857.33 | 1.22 | -10.9% | 9.38 | 1.21 |
| HYPE | 170 | 36.0% | 728.21 | 0.69 | -10.6% | 4.28 | 1.09 |
| **Combined** | **562** | **33.5%** | **-150.34** | **0.06** | **-9.4%** | **-0.27** | — |

Fees: total $4822.07.
Exits: {'stop': 484, 'signal': 78}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Breakeven scratch, 562 trades, -$150.34, PF 0.99. ETH +$1,857.33 (PF 1.21) and HYPE +$728.21 (PF 1.09) green, but BTC -$2,735.88 (PF 0.68) gives it all back; 484/562 exits hit the ATR stop.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
