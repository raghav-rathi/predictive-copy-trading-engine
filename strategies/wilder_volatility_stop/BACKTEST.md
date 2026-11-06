# Wilder Volatility Stop — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793973600000] (2026-03-14 22:00 UTC →
2026-11-06 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5681, ETH 5681, HYPE 5679.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 179 | 35.2% | -671.29 | -0.35 | -17.8% | -3.75 | 0.92 |
| ETH | 175 | 36.0% | -223.19 | -0.06 | -16.0% | -1.28 | 0.97 |
| HYPE | 164 | 36.0% | 893.73 | 0.86 | -11.4% | 5.45 | 1.11 |
| **Combined** | **518** | **35.7%** | **-0.75** | **0.16** | **-11.3%** | **-0.00** | — |

Fees: total $4530.90.
Exits: {'stop': 496, 'signal': 22}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Breakeven scratch combined, 518 trades, -$0.75, PF 1.00. HYPE's +$893.73 (PF 1.11) is the only green coin, offset almost exactly by BTC/ETH losses; 96% of exits are stops — the trailing-stop flips churn without capturing trend.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
