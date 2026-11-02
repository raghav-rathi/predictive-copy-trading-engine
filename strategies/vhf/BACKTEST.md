# VHF Trend Regime — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793628000000] (2026-03-14 22:00 UTC → 2026-11-02
14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 42 bars.

**Bar counts used:** BTC 5585, ETH 5585, HYPE 5583.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 146 | 25.3% | -2,944.54 | -2.97 | -30.4% | -20.17 | 0.54 |
| ETH | 147 | 34.7% | -2,295.52 | -2.09 | -26.2% | -15.62 | 0.66 |
| HYPE | 122 | 38.5% | +874.02 | +0.82 | -9.2% | +7.16 | 1.16 |
| **Combined** | **415** | **32.5%** | **-4,366.04** | **-1.85** | **-16.1%** | **-10.52** | **0.76** |

Fees: BTC $1,388.98, ETH $1,085.25, HYPE $648.96 (total $3,123.19).
Exits: 342 stop / 73 signal.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-4,366.04 across 415 trades on $30k starting capital, green only on HYPE. The regime filter arrives too late and exits too late. VHF Trend Regime is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
