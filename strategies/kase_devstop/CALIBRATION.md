# Kase DevStop — Calibration

Band std-multiplier sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-18, same costs/sizing,
6xATR disaster stop, no trail, 300-bar max hold). The sweep re-runs
`add_indicators(df, k=X)` only — signals and risk are unchanged.
The 1.0 row is the shipped Kase default.

| Std mult | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 0.5 | BTC | 514 | 34.4% | -$1,855 | -3.00 | 0.75 | -$3.61 |
| 0.5 | ETH | 508 | 34.4% | -$1,019 | -1.39 | 0.86 | -$2.01 |
| 0.5 | HYPE | 471 | 37.6% | +$51 | +0.15 | 1.01 | +$0.11 |
| 0.5 | **Combined** | **1,493** | — | **-$2,824** | — | — | — |
| 1.0 (shipped) | BTC | 390 | 32.3% | -$1,812 | -2.88 | 0.72 | -$4.65 |
| 1.0 (shipped) | ETH | 360 | 36.4% | -$388 | -0.42 | 0.93 | -$1.08 |
| 1.0 (shipped) | HYPE | 371 | 37.7% | +$399 | +0.65 | 1.07 | +$1.08 |
| 1.0 (shipped) | **Combined** | **1,121** | — | **-$1,800** | — | — | — |
| 1.5 | BTC | 284 | 36.6% | -$489 | -0.63 | 0.91 | -$1.72 |
| 1.5 | ETH | 286 | 34.3% | -$692 | -0.89 | 0.87 | -$2.42 |
| 1.5 | HYPE | 309 | 33.7% | +$102 | +0.21 | 1.02 | +$0.33 |
| 1.5 | **Combined** | **879** | — | **-$1,079** | — | — | — |

## One-line verdict

- **0.5 std:** the churn setting — 1,493 trades, combined -$2,824.
  A half-std band is inside ordinary 1h noise; the stop gets tagged
  constantly and the system bleeds fees ($3,010 total) on top of
  small losses.
- **1.0 std (shipped):** 1,121 trades, combined -$1,800. Still
  over-trading, still red on BTC/ETH, HYPE barely green.
- **1.5 std:** the least-bad row (-$1,079, 879 trades) — wider bands
  cut the whipsaw rate and BTC's loss by ~73% (-$489 vs -$1,812),
  but ETH gets worse (-$692) and nothing turns green. Widening helps
  the symptom, not the disease: a DevStop that flips 4+ times a day
  per coin is not a trend-following stop on this timeframe, whatever
  the multiplier.
- **Shipped decision:** keep the specified Kase default (1.0 std,
  DTR 30) as the registry config regardless. It was fixed before any
  backtest was run from the published source, and leaning toward 1.5
  std *because* it loses least in-sample would be in-sample
  selection on a 7-month window where no setting is green. The
  honest read: the band multiplier moves the loss, not the sign —
  the published DevStop does not work as a standalone flip system on
  1h crypto, and that still needs out-of-sample evidence to overturn.
