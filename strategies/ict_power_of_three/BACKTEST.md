# ICT Power of Three — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794574800000) (2026-03-14 22:00 UTC →
2026-11-13 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5847, ETH 5847, HYPE 5845.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 100 | 33.0% | -2026.39 | -3.04 | -24.5% | -20.26 | 0.42 |
| ETH | 97 | 40.2% | -634.56 | -0.67 | -14.7% | -6.54 | 0.79 |
| HYPE | 102 | 43.1% | -1056.97 | -1.78 | -17.6% | -10.36 | 0.70 |
| **Combined** | **299** | **38.8%** | **-3717.92** | **-2.41** | **-16.3%** | **-12.43** | **0.63** |

Fees: total $2289.87.
Exits: BTC {'signal': 68, 'stop': 32}; ETH {'signal': 66, 'stop': 31}; HYPE {'signal': 71, 'stop': 31}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$26,282.08.

## Verdict: LOSER — -$3,717.92 on 299 trades, combined Sharpe -2.41, MaxDD -16.3%.

Power of Three loses on all three coins: BTC -$2,026.39 (PF 0.42,
the worst per-coin PF in this batch), ETH -$634.56 (PF 0.79),
HYPE -$1,056.97 (PF 0.70). Win rate 38.8% with PF 0.63 does not
clear $2,289.87 in fees. The exit split is the honest tell in the
other direction from the batch's other losers: 205 of 299 trades
ended on the day-end signal exit, so the system really is trading
the AMD template as written — and the template does not pay on 1h
crypto in this window. The sweep-plus-reclaim sequence fires about
once a day per coin (~100 trades per coin over ~243 days), but the
reclaim more often marks a range that keeps ranging than the start
of a distribution leg. The UTC-day adaptation is the prime suspect:
ICT's AMD is a session-timing phenomenon (Asian range, London
sweep, New York distribution), and fixed UTC hour blocks on a
24/7 market do not reproduce that liquidity cycle.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 299-trade sample: a real sample, and the loss is consistent
  across all three coins — this is a system-level failure, not
  one bad coin.
- The UTC-day adaptation is untested against the session-based
  original; the result above is a verdict on the adaptation, not
  on ICT's AMD as traded in FX/indices sessions.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
