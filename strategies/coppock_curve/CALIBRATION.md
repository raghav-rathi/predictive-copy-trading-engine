# Coppock Curve — Calibration

WMA-length sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-21 13:00 UTC, same
costs/sizing, 2xATR stop, 3xATR trail, 200-bar max hold). The sweep
re-runs `add_indicators(df, wma_n=X)` only — signals and risk are
unchanged.

| WMA | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 7 | BTC | 312 | 30.1% | -$2,393 | -1.43 | 0.82 | -$7.67 |
| 10 (shipped) | BTC | 263 | 30.0% | -$2,314 | -1.41 | 0.80 | -$8.80 |
| 15 | BTC | 221 | 31.7% | -$2,179 | -1.37 | 0.79 | -$9.86 |
| 7 | ETH | 316 | 32.0% | -$1,349 | -0.69 | 0.90 | -$4.27 |
| 10 (shipped) | ETH | 276 | 31.2% | -$1,311 | -0.70 | 0.90 | -$4.75 |
| 15 | ETH | 235 | 32.8% | -$716 | -0.27 | 0.94 | -$3.05 |
| 7 | HYPE | 272 | 37.5% | +$3,684 | +1.90 | 1.24 | +$13.54 |
| 10 (shipped) | HYPE | 240 | 36.7% | +$3,089 | +1.70 | 1.21 | +$12.87 |
| 15 | HYPE | 220 | 36.4% | +$2,807 | +1.63 | 1.21 | +$12.76 |

## One-line verdict

- **7:** most reactive, most trades; best on HYPE (+$3,684, Sharpe
  +1.90) but worst on BTC (-$2,393). Reactivity helps the trending
  coin, costs the choppiest.
- **10 (shipped):** middle everywhere — worst HYPE leg of the three
  (+$3,089) and still red on BTC/ETH.
- **15:** smoothest, fewest trades; least-bad on BTC (-$2,179) and
  ETH (-$716), weakest on HYPE (+$2,807). Smoothing trades HYPE
  edge for smaller BTC/ETH losses.
- **Shipped decision:** keep the canonical WMA length=10 as the
  registry config regardless. The 10 was fixed before any backtest
  was run; the sweep does not produce a positive BTC or ETH read at
  any setting, so there is nothing to adopt — the in-sample
  "winner" (7 on HYPE, 15 on BTC/ETH) is a three-way split, and the
  right parameter (if this strategy deserves one) needs
  walk-forward or out-of-sample evidence, not this 7-month window.
