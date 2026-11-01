# RVI Cross — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793538000000] (2026-03-14 22:00 UTC → 2026-11-01
13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 20 bars.

**Bar counts used:** BTC 5560, ETH 5560, HYPE 5558.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 1035 | 31.0% | -8,361.16 | -8.57 | -84.0% | -8.08 | 0.56 |
| ETH | 1015 | 34.8% | -6,517.13 | -4.74 | -68.6% | -6.42 | 0.69 |
| HYPE | 960 | 34.1% | -6,109.96 | -4.54 | -64.1% | -6.36 | 0.71 |
| **Combined** | **3010** | **33.3%** | **-20,988.25** | **-1.60** | **-71.3%** | **-6.97** | **0.66** |

Fees: BTC $5,592.79, ETH $5,337.17, HYPE $3,091.62 (total $14,021.58).
Exits: 2074 signal / 936 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-20,988.25 across 3010 trades on $30k starting capital, loses on all three coins.
RVI Cross is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
