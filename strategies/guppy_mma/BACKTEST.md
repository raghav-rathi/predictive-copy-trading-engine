# Guppy MMA — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793538000000] (2026-03-14 22:00 UTC → 2026-11-01
13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 70 bars.

**Bar counts used:** BTC 5560, ETH 5560, HYPE 5558.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 179 | 33.5% | -1,158.27 | -0.85 | -19.5% | -6.47 | 0.85 |
| ETH | 215 | 28.8% | -1,343.06 | -0.96 | -22.2% | -6.25 | 0.86 |
| HYPE | 188 | 31.9% | +2,503.22 | +1.68 | -11.8% | +13.32 | 1.29 |
| **Combined** | **582** | **31.3%** | **+1.89** | **+1.24** | **-11.8%** | **+0.00** | **1.00** |

Fees: BTC $2,094.16, ETH $1,957.60, HYPE $1,105.43 (total $5,157.19).
Exits: 448 stop / 134 signal.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Breakeven, not an edge

+1.89 across 582 trades on $30k starting capital, green only on HYPE.
Guppy MMA is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
