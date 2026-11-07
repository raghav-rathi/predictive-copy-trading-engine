# Chaikin Oscillator — Backtest

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
| BTC | 341 | 29.6% | -3330.21 | -2.54 | -34.1% | -9.77 | 0.70 |
| ETH | 367 | 31.9% | -3501.45 | -2.84 | -41.0% | -9.54 | 0.69 |
| HYPE | 295 | 28.5% | -2581.85 | -2.00 | -30.3% | -8.75 | 0.73 |
| **Combined** | **1003** | **30.1%** | **-9413.51** | **-3.53** | **-33.2%** | **-9.39** | **0.70** |

Fees: total $7031.52.
Exits: {'signal': 604, 'stop': 399}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Heavy loser, 1003 trades, -$9413.51, PF 0.70 — the worst
leg of batch 29 by dollars. Red on all three coins (BTC -$3330.21,
ETH -$3501.45, HYPE -$2581.85) with ~30% win rates and combined
Sharpe -3.53 / MaxDD -33.2%. The zero-cross signal whipsaws: CHO
crosses zero constantly on 1h noise, so the strategy churns 1003
trades and pays $7031.52 in fees alone. The reverse-cross exit
(604 signal exits) flips positions almost as fast as it opens them.
A raw zero cross with no smoothing, confirmation, or divergence
filter has no edge here — the oscillator needs a filter the spec
does not have, and none was added (no PnL tuning).

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
