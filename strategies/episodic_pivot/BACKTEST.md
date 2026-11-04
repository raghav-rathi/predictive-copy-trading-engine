# Episodic Pivot — Backtest

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
| BTC | 0 | 0.0% | 0.00 | 0.00 | 0.0% | 0.00 | 0.00 |
| ETH | 0 | 0.0% | 0.00 | 0.00 | 0.0% | 0.00 | 0.00 |
| HYPE | 0 | 0.0% | 0.00 | 0.00 | 0.0% | 0.00 | 0.00 |
| **Combined** | **0** | **0.0%** | **0.00** | **0.00** | **0.0%** | **0.00** | — |

Fees: total $0.00.
Exits: {}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: No trades on any coin — not a loss, an untestable port. The setup needs a session gap (>=2% open vs prior close); 1h Hyperliquid candles are continuous (max observed gap 1.43% on HYPE, mean ~0.002-0.007%), so the trigger can never fire. Needs daily/session-based data to be testable at all.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
