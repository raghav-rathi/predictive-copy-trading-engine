# Chaikin Volatility Expansion — Calibration

Trigger sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, ms `[1773446400000, 1792627199000)`, same costs/sizing,
2xATR stop, 1.5xATR trail, 100-bar max hold). The sweep re-runs
`add_signals(df, trigger=X)` only — indicators and risk are unchanged.

| Trigger | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 2.5 | BTC | 307 | 32.2% | -$2,882 | -2.82 | 0.66 | -$9.39 |
| 2.5 | ETH | 323 | 31.0% | -$4,314 | -5.47 | 0.47 | -$13.35 |
| 2.5 | HYPE | 358 | 36.9% | -$2,755 | -3.33 | 0.68 | -$7.70 |
| 5.0 (shipped) | BTC | 305 | 32.5% | -$3,051 | -3.07 | 0.63 | -$10.00 |
| 5.0 (shipped) | ETH | 315 | 32.7% | -$3,831 | -4.50 | 0.53 | -$12.16 |
| 5.0 (shipped) | HYPE | 353 | 37.4% | -$3,062 | -3.86 | 0.64 | -$8.67 |
| 10.0 | BTC | 310 | 30.0% | -$3,506 | -3.70 | 0.56 | -$11.31 |
| 10.0 | ETH | 309 | 33.7% | -$3,418 | -3.87 | 0.59 | -$11.06 |
| 10.0 | HYPE | 324 | 37.3% | -$2,529 | -3.30 | 0.67 | -$7.81 |

Combined net by trigger: **2.5 → -$9,951; 5.0 → -$9,944; 10.0 → -$9,453.**

## One-line verdict

- **trigger=2.5:** the churn setting — most trades (988 combined),
  catches expansions earlier and pays the full climactic range;
  worst ETH leg (-$4,314, PF 0.47).
- **trigger=10.0:** the least-bad setting (combined -$9,453) — fewer
  HYPE trades (324 vs 353), slightly better HYPE leg (-$2,529), but
  the worst BTC leg (-$3,506) and the best coin-pair spread of the
  three, which is in-sample noise across a uniformly red surface.
- **trigger=5.0:** mid-pack on every coin — combined -$9,944.
- **Shipped decision:** keep the specified trigger=5.0 regardless. The
  trigger was fixed before any backtest was run, and the sweep
  contains no in-sample winner to select: all three settings lose on
  all three coins, and the $500 spread between the best and worst
  combined setting is noise on a ~$10k combined loss. Leaning toward
  trigger=10.0 *because* it is marginally less red would be in-sample
  selection on a strategy whose premise (trading with the trend into
  volatility expansion) the data rejects at every setting. The honest
  read: the entry hypothesis is wrong, not the threshold — the
  threshold cannot fix a reversal signal being traded as a
  continuation signal.
