# Chande Dynamic Momentum Index — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`); `fetch_candles` was NOT
called, so the cache was not extended past the window. Window t in
[1773525600000, 1794315600000) (2026-03-14 22:00 UTC →
2026-11-10 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 45 bars.

**Bar counts used:** BTC 5775, ETH 5775, HYPE 5773. Before dedup the
window held 5780 / 5780 / 5778 rows, i.e. 5 exact-duplicate bars per
coin were dropped. First bar BTC/ETH 1773525600000 (2026-03-14 22:00
UTC), HYPE 1773532800000 (2026-03-15 00:00 UTC); last bar all coins
1794315600000 (2026-11-10 13:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 365 | 41.9% | -3014.64 | -2.01 | -36.8% | -8.26 | 0.81 |
| ETH | 336 | 43.5% | -1056.34 | -0.56 | -21.5% | -3.14 | 0.92 |
| HYPE | 352 | 40.9% | -3706.66 | -2.94 | -39.6% | -10.53 | 0.74 |
| **Combined** | **1053** | **42.1%** | **-7777.64** | **-2.52** | **-30.1%** | **-7.39** | **0.82** |

Fees: total $7344.29 (BTC $3468.15, ETH $2446.53, HYPE $1429.62).
Exits: BTC {'stop': 233, 'signal': 132}; ETH {'stop': 211, 'signal': 125}; HYPE {'stop': 227, 'signal': 125}. No target or max-hold exits (target is off; max hold never bound first). Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k); combined end equity $22,187.47.

## Verdict: Loser on all three coins (−$7,777.64 combined, PF 0.82, Sharpe −2.52).

The DMI fires 1,053 trades in ~8 months — roughly 4–5 per day per coin — and loses on every coin: BTC −$3,014.64, ETH −$1,056.34, HYPE −$3,706.66. The dynamic lookback does not buy whipsaw immunity on 1h crypto: 671 of 1,053 exits (64%) are ATR stops, and the 42.1% win rate with PF 0.82 is a losing system before fees; after $7,344.29 of fees it is decisively negative, with a combined −30.1% max drawdown and HYPE at −39.6%. The RSI-style 30/70 cross rules mean-revert into trends that keep running, and the exits (opposite-extreme crosses) arrive too late to save the stops. Not a tradeable signal as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- DMI levels 30/70 are the classic RSI thresholds applied per
  Chande's "use it much the same as the RSI" guidance; no other
  threshold was tried.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
