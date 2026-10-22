# DEMA Trend Cross — Calibration

Fast/slow sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same costs/sizing, 2xATR stop,
2.5xATR trail, 200-bar max hold). The sweep re-runs
`add_indicators(df, fast=X, slow=Y)` only — signals and risk are
unchanged.

| Fast/Slow | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10/30 | BTC | 311 | 28.9% | -$3,067 | -2.11 | 0.77 | -$9.86 |
| 10/30 | ETH | 330 | 30.3% | -$2,136 | -1.31 | 0.84 | -$6.47 |
| 10/30 | HYPE | 307 | 35.5% | +$2,710 | +1.56 | 1.19 | +$8.83 |
| 21/55 (shipped) | BTC | 169 | 36.7% | -$1,102 | -0.70 | 0.85 | -$6.52 |
| 21/55 (shipped) | ETH | 164 | 33.5% | +$544 | +0.51 | 1.06 | +$3.32 |
| 21/55 (shipped) | HYPE | 181 | 35.4% | -$74 | +0.05 | 0.99 | -$0.41 |
| 34/89 | BTC | 103 | 31.1% | -$997 | -1.02 | 0.78 | -$9.68 |
| 34/89 | ETH | 109 | 33.0% | -$968 | -0.97 | 0.82 | -$8.88 |
| 34/89 | HYPE | 101 | 36.6% | -$705 | -0.64 | 0.85 | -$6.98 |

Combined per setting: (10,30) **-$2,494**; (21,55) **-$632**;
(34,89) **-$2,670**.

## One-line verdict

- **(10,30):** the chop setting — 311 BTC trades, -$3,067 on BTC
  alone (expectancy -$9.86/trade), Sharpe -2.11. Faster DEMAs react
  to every wiggle; HYPE is the only green coin (+$2,710, the one
  genuinely positive cell in the whole sweep). Combined -$2,494.
- **(34,89):** fewer trades (101–109 per coin), fewer whipsaws, still
  red on all three coins. Slower crosses miss the chop but also miss
  the legs that pay for it. Combined -$2,670, the worst of the three.
- **(21,55):** least-bad combined (-$632) — BTC still loses -$1,102,
  HYPE flat, ETH +$544 near-noise — but that is an in-sample
  observation, not a justification.
- **Shipped decision:** keep the specified (21,55) as the registry
  config regardless. The (21,55) pair was fixed a priori — adopted
  before the sweep, not because of it — so no in-sample selection
  was performed. The honest read: no setting on this window makes
  DEMA crosses a viable 1h strategy; the parameter moves which coin
  loses, not whether the strategy works. That verdict stands until
  walk-forward or out-of-sample evidence says otherwise.
