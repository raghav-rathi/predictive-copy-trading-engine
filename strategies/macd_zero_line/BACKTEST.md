# MACD Zero-Line Cross — Backtest

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
| BTC | 195 | 31.3% | -2148.13 | -1.69 | -25.5% | -11.02 | 0.74 |
| ETH | 217 | 31.8% | -361.92 | -0.11 | -25.3% | -1.67 | 0.96 |
| HYPE | 182 | 36.8% | 917.96 | 0.73 | -9.8% | 5.04 | 1.10 |
| **Combined** | **594** | **33.2%** | **-1592.08** | **-0.42** | **-14.6%** | **-2.68** | **0.94** |

Fees: total $5041.86.
Exits: {'stop': 505, 'signal': 89}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 594 trades, -$1,592.08, PF 0.94 — the
zero-line cross whipsaws badly in this window: 85% of exits are the
2xATR stop, not the reverse cross, so positions get stopped out
before the momentum flip the system is built to ride. HYPE (+$917.96)
is the only green coin; BTC (-$2,148.13) carries the loss. Win rate
33.2% with expectancy -$2.68/trade — no edge here, reported as-is.

## Limitations

- Single ~7.7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
