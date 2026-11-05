# Kaufman's Adaptive Moving Average — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793887200000] (2026-03-14 22:00 UTC →
2026-11-05 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5656, ETH 5656, HYPE 5654.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 758 | 21.0% | -6740.18 | -5.38 | -69.2% | -8.89 | 0.60 |
| ETH | 818 | 22.0% | -4828.03 | -3.01 | -52.6% | -5.90 | 0.77 |
| HYPE | 775 | 24.0% | -3781.52 | -2.22 | -41.2% | -4.88 | 0.79 |
| **Combined** | **2351** | **22.4%** | **-15349.73** | **-5.07** | **-52.9%** | **-6.53** | — |

Fees: total $13310.48.
Exits: {'signal': 1548, 'stop': 803}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Big loser, 2351 trades, -$15,349.73, PF 0.73. Win rate only 22.4% — the adaptive average hugs price in chop and the cross entries fire on every wiggle; $13,310.48 in fees on 2,343+ churn trades.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
