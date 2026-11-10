# Fisher ACD Opening Range — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794315600000) (2026-03-14 22:00 UTC →
2026-11-10 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. Max hold 24 bars, 2.5xATR chandelier trail.

**Bar counts used:** BTC 5775, ETH 5775, HYPE 5773.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 415 | 29.4% | -6225.19 | -4.52 | -63.0% | -15.00 | 0.58 |
| ETH | 435 | 29.9% | -5655.23 | -3.56 | -61.1% | -13.00 | 0.63 |
| HYPE | 392 | 33.9% | -3614.63 | -2.15 | -37.0% | -9.22 | 0.77 |
| **Combined** | **1242** | **31.0%** | **-15495.05** | **-4.39** | **-53.2%** | **-12.48** | **0.66** |

Fees: total $6886.96.
Exits: BTC {'stop': 304, 'signal': 76, 'max_hold': 35}; ETH {'stop': 331, 'signal': 64, 'max_hold': 40}; HYPE {'stop': 278, 'signal': 75, 'max_hold': 39}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$14,524.80.

## Verdict: Clear loser on paper (−$15,495.05, PF 0.66, Sharpe −4.39).

Fisher ACD as adapted here loses badly on 1h crypto. The opening range
is a single 1h bar, so it is far too narrow to carry a day's tone: the
A points (OR edge ± 0.5 ATR) are crossed on most days and the system
fires ~1,240 trades in ~8 months (~5/day across the three coins), with
913 of 1,242 exits (73.5%) dying on the ATR stop and only 215 on the
B-point signal exit. Win rate 31.0% with PF 0.66 means the average
winner does not cover the average loser even before the $6,886.96 of
fees; BTC alone loses −$6,225.19 (−62% of its $10k start) with a −63.0%
drawdown, and every coin is negative. The C-level reversals add churn
rather than rescue: a close beyond C is usually momentum exhaustion
into the stop, not a clean reversal. Not a tradeable signal as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The 1h-bar opening range is a much weaker session proxy than Fisher's
  original pit-session opening range; crypto trades 24/7 with no true
  open, so the UTC-day boundary is arbitrary.
- The daily pivot is undefined on the first (partial) UTC day of the
  window, so no A-point entries can fire there; HYPE's first day in the
  window is a full UTC day with no pivot (its cache starts 2026-03-15
  00:00 UTC).
- Never tune the shipped parameters on this window.

Paper only, no live execution.
