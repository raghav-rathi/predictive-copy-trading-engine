# FVG Mitigation — Backtest

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
| BTC | 220 | 36.4% | -1,731.41 | -1.11 | -18.8% | -7.87 | 0.83 |
| ETH | 250 | 34.8% | -501.57 | -0.18 | -21.3% | -2.01 | 0.96 |
| HYPE | 226 | 38.9% | +3,406.46 | +1.91 | -14.2% | +15.07 | 1.27 |
| **Combined** | **696** | **36.6%** | **+1,173.48** | **+1.33** | **-14.3%** | **+1.69** | **1.03** |

Fees: BTC $2,116.89, ETH $2,058.90, HYPE $1,409.10 (total $5,584.89).
Exits: 695 stop / 1 max_hold.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Breakeven, not an edge

+1,173.48 across 696 trades on $30k starting capital, green only on HYPE.
FVG Mitigation is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
