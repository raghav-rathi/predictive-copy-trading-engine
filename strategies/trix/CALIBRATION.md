# TRIX Momentum Turn — Calibration

Length sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same costs/sizing, 2xATR stop,
3xATR trail, 200-bar max hold). The sweep re-runs
`add_indicators(df, n=X)` only — signals and risk are unchanged. The
sweep ran with END=1792589130654 (same 1h candle set as the main run).

| Length | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 239 | 33.5% | -$3,878 | -3.29 | 0.64 | -$16.23 |
| 10 | ETH | 244 | 33.6% | -$2,439 | -1.77 | 0.79 | -$9.99 |
| 10 | HYPE | 237 | 37.1% | +$2,623 | +1.59 | 1.19 | +$11.07 |
| 14 (shipped) | BTC | 180 | 38.3% | -$724 | -0.34 | 0.92 | -$4.02 |
| 14 (shipped) | ETH | 182 | 37.4% | +$441 | +0.42 | 1.04 | +$2.42 |
| 14 (shipped) | HYPE | 183 | 43.7% | +$5,573 | +2.94 | 1.50 | +$30.45 |
| 21 | BTC | 131 | 43.5% | +$1,463 | +1.17 | 1.21 | +$11.17 |
| 21 | ETH | 137 | 35.0% | -$233 | -0.03 | 0.97 | -$1.70 |
| 21 | HYPE | 136 | 39.0% | +$2,310 | +1.65 | 1.30 | +$16.98 |

## One-line verdict

- **len=10:** the chop setting — 239 BTC trades, -$3,878 on BTC
  alone (expectancy -$16/trade), combined -$3,694. Shorter
  triple-EMAs still wiggle enough to fire bad turns; the only green
  coin is HYPE.
- **len=21:** the best BTC read in the whole exercise (+$1,463,
  Sharpe +1.17, PF 1.21 — slower turns, fewer whipsaws) but the worst
  HYPE read (+$2,310, less than half the shipped setting) and ETH
  flips red (-$233). Combined +$3,540.
- **len=14:** best combined (+$5,290) and the only setting
  positive-or-flat on all three coins — but that is an in-sample
  observation, not a justification.
- **Shipped decision:** keep the specified len=14 as the registry
  config regardless. The len=14 length was fixed before any backtest
  was run; the in-sample ranking does not change that, and leaning
  toward len=21 *because* it rescues BTC would be in-sample
  selection against a 7-month window where HYPE carried everything
  anyway. The honest read: the length moves which coin pays, not
  whether the strategy works — that still needs walk-forward or
  out-of-sample evidence.
