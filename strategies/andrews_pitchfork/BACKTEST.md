# Andrews Pitchfork — Backtest

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
| BTC | 268 | 44.8% | -2621.85 | -2.19 | -28.1% | -9.78 | 0.74 |
| ETH | 269 | 40.1% | -2417.37 | -1.98 | -27.4% | -8.99 | 0.78 |
| HYPE | 257 | 43.2% | -2092.10 | -1.78 | -29.8% | -8.14 | 0.81 |
| **Combined** | **794** | **42.7%** | **-7131.32** | **-3.16** | **-25.1%** | **-8.98** | **0.78** |

Fees: total $5761.24.
Exits: {'stop': 501, 'signal': 293}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Clear loser combined, 794 trades, -$7,131.32, PF 0.78 —
the worst batch-29 strategy by dollars and by Sharpe (-3.16). All
three coins lose heavily and consistently (BTC -$2,621.85, ETH
-$2,417.37, HYPE -$2,092.10), so this is not a one-coin artifact.
Median-line targets are reached often enough (293 signal exits) but
the 0.25x ATR touch band fires on nearly every dip toward a
fast-moving fork line, and 501 stop exits show the bounces keep
failing through the parallel. The fork recomputes on every new pivot
triple, so the "line" a trade entered on is frequently not the line it
is judged against a few bars later.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
