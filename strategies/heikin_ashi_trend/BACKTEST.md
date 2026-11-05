# Heikin Ashi Trend — Backtest

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
| BTC | 817 | 22.0% | -8366.79 | -9.15 | -84.0% | -10.24 | 0.44 |
| ETH | 882 | 24.0% | -8082.40 | -7.60 | -81.1% | -9.16 | 0.51 |
| HYPE | 781 | 30.0% | -5614.51 | -4.36 | -56.2% | -7.19 | 0.66 |
| **Combined** | **2480** | **25.3%** | **-22063.70** | **-10.00** | **-73.7%** | **-8.90** | — |

Fees: total $11102.13.
Exits: {'signal': 1871, 'stop': 609}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins, 2480 trades, PF 0.44-0.66. The 2-green-after-red trigger fires constantly in chop (781-882 trades per coin) and exiting on the first opposite-colour HA candle cuts winners before the EMA50 trend can pay; the strategy churns itself to death on fees ($11,102.13) plus stop losses.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
