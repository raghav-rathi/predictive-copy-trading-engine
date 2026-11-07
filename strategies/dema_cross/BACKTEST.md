# DEMA Crossover — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail. Window t in [1773525600000, 1794060000000]
(2026-03-14 22:00 UTC → 2026-11-07 13:00 UTC, last completed hour
bar; coordinator-verified on the fixed window, excluding the partial
14:00 UTC bar the standard runner pulls). $10k start per
coin, 1% risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee
+ 0.01% slippage per side, funding off.

**Bar counts used:** BTC 5704, ETH 5704, HYPE 5702.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 319 | 31.3% | -2533.31 | -1.51 | -34.2% | -7.94 | 0.81 |
| ETH | 334 | 32.0% | -1719.07 | -0.91 | -29.5% | -5.15 | 0.88 |
| HYPE | 314 | 37.3% | 2933.95 | 1.58 | -16.2% | 9.34 | 1.19 |
| **Combined** | **967** | **33.5%** | **-1318.43** | **-0.22** | **-16.1%** | **-1.36** | **0.97** |

Fees: total $7872.92.
Exits: {'stop': 686, 'signal': 281}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 967 trades, -$1,318.43, PF 0.97 — near
breakeven, and the only batch-29 strategy with a winning coin: HYPE
+$2,933.95 (37.3% win rate, PF 1.19, Sharpe 1.58) carries the book
while BTC (-$2,533.31) and ETH (-$1,719.07) drag it under. The
crossover is a lagging trend system on 1h noise: 33.5% win rate and
686 of 967 exits are stops, not signal exits — positions are usually
stopped out before the reverse cross arrives. The HYPE win is a
single-coin, single-window result, not evidence of an edge; combined
expectancy is -$1.36/trade.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
