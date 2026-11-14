# Sine-Weighted MA Trend — Calibration

Length sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-18, same costs/sizing, 2xATR stop,
3xATR trail, 200-bar max hold). The sweep re-runs
`add_indicators(df, fast_n=X, slow_n=Y)` only — signals and risk are
unchanged.

| Length | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10/20 | BTC | 311 | 37.0% | -$1,781 | -1.00 | 0.87 | -$5.73 |
| 10/20 | ETH | 348 | 32.5% | -$2,116 | -1.16 | 0.87 | -$6.08 |
| 10/20 | HYPE | 311 | 37.3% | +$2,739 | +1.54 | 1.17 | +$8.81 |
| 20/40 (shipped) | BTC | 159 | 30.8% | -$1,919 | -1.51 | 0.74 | -$12.07 |
| 20/40 (shipped) | ETH | 169 | 40.2% | +$1,132 | +0.84 | 1.15 | +$6.70 |
| 20/40 (shipped) | HYPE | 160 | 36.2% | +$1,487 | +1.11 | 1.19 | +$9.29 |
| 30/60 | BTC | 107 | 40.2% | +$1,056 | +0.97 | 1.24 | +$9.87 |
| 30/60 | ETH | 113 | 31.0% | -$938 | -0.77 | 0.84 | -$8.30 |
| 30/60 | HYPE | 113 | 28.3% | -$2,509 | -2.50 | 0.55 | -$22.20 |

## One-line verdict

- **10/20:** the chop setting — 311–348 trades per coin, combined
  -$1,159. Faster crosses fire twice as often and lose on BTC and ETH;
  only HYPE stays green.
- **30/60:** fixes BTC (+$1,056, Sharpe +0.97, PF 1.24) but destroys
  HYPE (-$2,509, Sharpe -2.50, expectancy -$22.20/trade) and flips ETH
  red. Combined -$2,391.
- **20/40 (shipped):** best combined (+$700) and the only setting
  green on two of three coins — but that is an in-sample observation,
  not a justification; +$700 on 488 trades is noise.
- **Shipped decision:** keep the specified 20/40 as the registry
  config regardless. The 20/40 lengths were fixed before any backtest
  was run; the in-sample ranking does not change that, and leaning
  toward 30/60 *because* it rescues BTC would be in-sample selection
  against a 7-month window where no setting works on all three coins.
  The honest read: the length moves which coin pays, not whether the
  strategy works — that still needs walk-forward or out-of-sample
  evidence.
