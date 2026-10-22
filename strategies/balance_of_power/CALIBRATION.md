# Balance of Power — Calibration

SMA-length sensitivity on the same local cache data as BACKTEST.md
(BTC/ETH/HYPE 1h, ms `[1773446400000, 1792627199000)`, same
costs/sizing, 2xATR stop, 2.5xATR trail, 150-bar max hold). The sweep
re-runs `add_indicators(df, n=X)` only — signals and risk unchanged.
n=14 was fixed A PRIORI (the StockCharts default, adopted before any
backtest); the sweep below is diagnostic only and no in-sample
selection was performed.

| Len | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 7 | BTC | 1,089 | 23.0% | -$8,337 | -9.06 | 0.52 | -$7.66 |
| 7 | ETH | 1,029 | 26.5% | -$6,275 | -4.76 | 0.67 | -$6.10 |
| 7 | HYPE | 997 | 28.9% | -$5,735 | -4.67 | 0.72 | -$5.75 |
| 14 (shipped) | BTC | 807 | 22.4% | -$7,236 | -6.97 | 0.57 | -$8.97 |
| 14 (shipped) | ETH | 769 | 25.4% | -$5,242 | -3.85 | 0.72 | -$6.82 |
| 14 (shipped) | HYPE | 688 | 31.0% | -$2,663 | -1.71 | 0.86 | -$3.87 |
| 28 | BTC | 551 | 25.2% | -$5,489 | -4.93 | 0.61 | -$9.96 |
| 28 | ETH | 591 | 21.3% | -$5,768 | -5.01 | 0.57 | -$9.76 |
| 28 | HYPE | 498 | 28.7% | -$2,915 | -2.04 | 0.78 | -$5.85 |

## One-line verdict

- **n=7:** the chop setting — ~1,000 trades per coin, combined
  -$20,347. A 7-bar BOP wiggles across zero constantly and pays the
  fee man on every wiggle (Sharpe -9.06 on BTC).
- **n=28:** the slow setting — fewer trades (551 BTC), still
  combined -$14,172. Slower crosses are even later to legs, so the
  entries miss more and the stops still bite; ETH's 21.3% win rate is
  the worst of the nine cells.
- **n=14 (shipped):** combined -$15,141 — the "best" combined number,
  but that is like being the least-leaky boat in a sunk fleet. The
  in-sample ranking moves only how much is lost, not whether the
  trigger works.
- **Shipped decision:** keep n=14. It was fixed before any backtest
  ran (StockCharts' default smoothing), and nothing in this table
  justifies changing it — leaning toward n=28 *because* its BTC leg
  loses a bit less would be in-sample selection on a losing
  strategy, which is selecting the best-looking loser instead of
  admitting the trigger itself is broken. The honest read: BOP as a
  zero-cross entry loses at every smoothing length tried — the
  length moves the size of the loss, not its sign.
