# Reflex Zero-Lag — Calibration

Length sensitivity on the same local 1h data as BACKTEST.md
(BTC/ETH/HYPE, ms `[1773446400000, 1792627199000)`, same costs/sizing,
2xATR stop, 2.5xATR trail, 150-bar max hold). The sweep re-runs
`add_indicators(df, length=X)` only — signals and risk are unchanged.
WARMUP=100 in all runs.

**The length=20 setting was fixed a priori — adopted before any
backtest ran, not selected from this sweep.** The sweep is a
sensitivity check only.

| Length | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 414 | 29.7% | -$3,161 | -2.00 | 0.79 | -$7.63 |
| 10 | ETH | 422 | 31.5% | -$3,097 | -1.89 | 0.80 | -$7.34 |
| 10 | HYPE | 392 | 34.7% | +$716 | +0.57 | 1.04 | +$1.83 |
| 20 (shipped) | BTC | 198 | 31.3% | -$2,290 | -1.73 | 0.73 | -$11.57 |
| 20 (shipped) | ETH | 208 | 33.2% | +$859 | +0.74 | 1.10 | +$4.13 |
| 20 (shipped) | HYPE | 201 | 37.8% | +$449 | +0.47 | 1.05 | +$2.23 |
| 40 | BTC | 102 | 46.1% | +$287 | +0.50 | 1.07 | +$2.82 |
| 40 | ETH | 112 | 33.9% | -$710 | -0.57 | 0.87 | -$6.34 |
| 40 | HYPE | 106 | 33.0% | -$970 | -1.00 | 0.78 | -$9.15 |

Combined: len=10 → 1,228 trades, -$5,542 (PF 0.88); len=20 →
607 trades, -$982 (PF 0.96); len=40 → 320 trades, -$1,392 (PF 0.90).

## One-line verdict

- **len=10:** the chop setting — 1,228 trades, -$5,542 combined,
  fees $9,691 vs net -$5,542. The zero-lag property at length 10 is
  just whipsaw; Reflex re-crosses faster than the 1h bars can trend.
- **len=40:** the slowest setting — only 320 trades, -$1,392
  combined. It fixes BTC (+$287, 46.1% win, the only BTC-green row
  anywhere) but wrecks HYPE (-$970) and leaves ETH red. The length
  moves which coin pays, not whether the strategy works.
- **len=20 (shipped):** least-bad in-sample (combined -$982,
  PF 0.96, the only setting with two of three coins positive) — but
  that is an in-sample observation, not a justification, and the
  combined ledger is still negative.
- **Shipped decision:** keep the specified length=20 as the registry
  config regardless. The length was fixed before any backtest ran;
  the in-sample ranking does not change that, and leaning toward
  len=40 *because* it rescues BTC would be in-sample selection
  against a window where nothing is convincingly green anyway. The
  honest read: every length is negative combined — the problem is
  the naked zero-cross entry on 1h chop, not the parameter.
