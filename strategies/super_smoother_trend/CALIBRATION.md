# SuperSmoother Trend — Calibration

Fast/slow sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, batch-45 window 2026-03-14 →
2026-11-24, ms `[1773525600000, 1795525200000)`, same
costs/sizing, 2xATR stop, 3xATR trail, 60-bar max hold). The
filter pair is the strategy's natural knob: (5,20) is fast and
twitchy (more crosses, more chop), (20,50) is slow and patient
(fewer crosses, later entries). The sweep re-runs
`add_indicators(df, fast_n=X, slow_n=Y)` only — signals and risk
are unchanged. Re-run on the batch-45 window with the pinned
runner's loader (local cache only); the Nov-14 sweep numbers
were superseded and are not retained here.

| fast/slow | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| (5,20) | BTC | 841 | 25.80% | -$7,938.47 | -6.44 | 0.56 | -$9.44 |
| (5,20) | ETH | 827 | 28.30% | -$5,872.03 | -3.39 | 0.72 | -$7.10 |
| (5,20) | HYPE | 803 | 30.88% | -$4,180.03 | -2.19 | 0.83 | -$5.21 |
| (10,30) (shipped) | BTC | 489 | 31.70% | -$2,557.31 | -1.14 | 0.85 | -$5.23 |
| (10,30) (shipped) | ETH | 525 | 28.57% | -$4,504.89 | -2.49 | 0.74 | -$8.58 |
| (10,30) (shipped) | HYPE | 472 | 36.23% | +$3,236.60 | +1.47 | 1.15 | +$6.86 |
| (20,50) | BTC | 282 | 32.62% | -$1,947.25 | -0.98 | 0.85 | -$6.91 |
| (20,50) | ETH | 288 | 32.29% | +$173.49 | +0.24 | 1.01 | +$0.60 |
| (20,50) | HYPE | 276 | 35.14% | +$1,424.77 | +0.85 | 1.09 | +$5.16 |

## One-line verdict

- **(5,20):** fastest pair, most trades (2,471) — catastrophic
  everywhere (combined -$17,990.52, BTC MaxDD -80.36%, Sharpe
  -6.44). A faster SuperSmoother just crosses more often on noise.
- **(20,50):** slowest pair, fewest trades (846) — least-bad
  combined (-$349.00), breakeven on ETH (+$173.49, PF 1.01) and
  positive on HYPE (+$1,424.77), still negative on BTC
  (-$1,947.25). Slower is better here, monotonically, which says
  the shipped pair is too fast for 1h crypto chop — but slower
  is still not a winner.
- **(10,30) (shipped):** middle of the pack (combined
  -$3,825.60), best on no coin, worst on no coin.
- **Shipped decision:** keep the specified SS(10)/SS(30) as the
  registry config regardless. It was fixed before any backtest
  was run; adopting (20,50) *because* it is least-bad in-sample
  would still be in-sample selection. The honest read: the knob
  is steep (combined net spans -$349.00 to -$17,990.52), which
  says crossover speed matters a lot — but even the best setting
  is net-negative combined, so the problem is the crossover
  premise on this timeframe, not just the periods.
