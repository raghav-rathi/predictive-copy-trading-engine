# Aroon Oscillator — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793628000000] (2026-03-14 22:00 UTC → 2026-11-02
14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 39 bars.

**Bar counts used:** BTC 5585, ETH 5585, HYPE 5583.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 255 | 35.7% | -2,354.03 | -1.72 | -27.6% | -9.23 | 0.75 |
| ETH | 260 | 36.2% | +501.84 | +0.44 | -19.8% | +1.93 | 1.04 |
| HYPE | 235 | 36.6% | -101.43 | +0.04 | -11.0% | -0.43 | 0.99 |
| **Combined** | **750** | **36.1%** | **-1,953.62** | **-0.54** | **-15.2%** | **-2.60** | **0.94** |

Fees: BTC $2,752.00, ETH $2,583.98, HYPE $1,227.75 (total $6,563.72).
Exits: 588 stop / 162 signal.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-1,953.62 across 750 trades on $30k starting capital, green only on ETH. The zero cross fires on every fresh extreme and pays for it in chop. Aroon Oscillator is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
