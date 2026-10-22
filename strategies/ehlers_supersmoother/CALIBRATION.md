# SuperSmoother Trend — Calibration

Period sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same costs/sizing, 2xATR stop,
2xATR trail, 150-bar max hold). The sweep re-runs
`add_indicators(df, period=X)` only — signals and risk are unchanged.

| Period | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 514 | 25.1% | -$5,821 | -7.10 | 0.46 | -$11.32 |
| 10 | ETH | 519 | 26.4% | -$3,545 | -3.03 | 0.69 | -$6.83 |
| 10 | HYPE | 507 | 29.8% | -$2,328 | -2.03 | 0.80 | -$4.59 |
| 20 (shipped) | BTC | 307 | 24.1% | -$3,482 | -3.83 | 0.60 | -$11.34 |
| 20 (shipped) | ETH | 304 | 27.3% | -$1,425 | -1.32 | 0.83 | -$4.69 |
| 20 (shipped) | HYPE | 303 | 27.4% | -$2,141 | -2.42 | 0.72 | -$7.06 |
| 40 | BTC | 216 | 20.8% | -$2,834 | -3.33 | 0.58 | -$13.12 |
| 40 | ETH | 226 | 21.2% | -$1,085 | -0.84 | 0.86 | -$4.80 |
| 40 | HYPE | 210 | 23.8% | -$1,923 | -2.33 | 0.66 | -$9.16 |

Combined net: period 10 → -$11,694 (1,540 trades); period 20 →
-$7,047 (914); period 40 → -$5,842 (652).

## One-line verdict

- **period=10:** the chop setting — 514 BTC trades, -$5,821 on BTC
  alone (Sharpe -7.10, -58.3% drawdown), combined -$11,694. The
  faster filter crosses constantly and pays fees on every wiggle.
- **period=40:** the least-bad setting (combined -$5,842) — slower
  filter, fewer trades, but still red on all three coins with the
  worst per-trade expectancy on BTC (-$13.12). Slower does not fix
  it, it just bleeds less often.
- **period=20:** red on all three coins (combined -$7,047). The
  period moves the size of the loss, not its sign — 9/9 cells
  negative.
- **Shipped decision:** keep the specified period=20 as the registry
  config regardless. The period was fixed a priori at Ehlers'
  canonical cutoff before any backtest was run, and the sweep is red
  everywhere, so there is no in-sample winner to chase — leaning
  toward period=40 *because* it loses the least would be
  in-sample selection against a 7-month window where nothing works.
  The honest read: the period is not the problem; filter-cross
  entries on 1h crypto have no edge at any tested cutoff.
