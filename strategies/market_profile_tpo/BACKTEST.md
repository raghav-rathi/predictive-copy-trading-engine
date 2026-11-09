# Market Profile TPO Value-Area Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794232800000) (2026-03-14 22:00 UTC →
2026-11-09 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5752, ETH 5752, HYPE 5750.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 124 | 33.1% | -1843.14 | -1.72 | -22.3% | -14.86 | 0.69 |
| ETH | 124 | 43.5% | 1058.64 | 0.86 | -13.8% | 8.54 | 1.17 |
| HYPE | 120 | 35.8% | 2573.98 | 1.77 | -7.7% | 21.45 | 1.39 |
| **Combined** | **368** | **37.5%** | **1789.48** | **0.71** | **-10.3%** | **4.86** | **1.10** |

Fees: total $3023.06.
Exits: {'stop': 368}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on BTC, winner on ETH/HYPE, combined +$1,789.48 (PF 1.10) — a marginal, unproven edge

The combined profit is real money on 368 trades, but it is thin
(PF 1.10, Sharpe 0.71) and entirely carried by HYPE (+$2,574) and
ETH (+$1,059) while BTC lost -$1,843 with a -22.3% drawdown. Every
single one of the 368 exits hit the ATR stop/trail — no trade ever
reached the opposite value-area-break signal exit, so the signal
exit is untested in practice and the strategy is really "buy/sell
VA breaks with a 2xATR stop and 2.5xATR trail". Treat as unproven /
not tradeable without a much larger sample and an out-of-sample
check.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
