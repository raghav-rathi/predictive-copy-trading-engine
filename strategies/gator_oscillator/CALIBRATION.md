# Gator Oscillator States — Calibration

Jaw-length sensitivity on the same local cache data as BACKTEST.md
(BTC/ETH/HYPE 1h, ms `[1773446400000, 1792627199000)`, same
costs/sizing, 2xATR stop, 3xATR trail, 150-bar max hold). The sweep
re-runs `add_indicators(df, ...)` only — signals and risk are
unchanged. Lengths and shifts are scaled from jaw_len keeping Bill
Williams' 13:8:5 and 8:5:3 ratios (rounded): jaw=8 → teeth/lips 5/3,
shifts 5/3/2; jaw=13 → 8/5, shifts 8/5/3; jaw=21 → 13/8, shifts 13/8/5.

| Jaw | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 8 | BTC | 491 | 33.8% | -$4,981 | -5.13 | 0.601 | -$10.14 |
| 8 | ETH | 480 | 39.0% | -$4,231 | -3.56 | 0.658 | -$8.81 |
| 8 | HYPE | 478 | 43.7% | -$2,932 | -2.48 | 0.782 | -$6.13 |
| 13 (shipped) | BTC | 338 | 40.2% | -$2,911 | -2.50 | 0.720 | -$8.61 |
| 13 (shipped) | ETH | 358 | 36.3% | -$2,997 | -2.42 | 0.733 | -$8.37 |
| 13 (shipped) | HYPE | 329 | 41.3% | -$1,630 | -1.31 | 0.853 | -$4.95 |
| 21 | BTC | 240 | 36.3% | -$3,179 | -3.03 | 0.620 | -$13.24 |
| 21 | ETH | 265 | 41.5% | -$2,796 | -2.66 | 0.673 | -$10.55 |
| 21 | HYPE | 231 | 38.5% | -$1,629 | -1.47 | 0.810 | -$7.05 |

## One-line verdict

- **jaw=8:** the chop setting — 1,449 trades combined (-$12,144),
  BTC alone -$4,981 with expectancy -$10.14/trade and PF 0.601. Faster
  balance lines flip states constantly and the fan filter keeps
  confirming noise.
- **jaw=21:** the calmest setting — fewest trades (736 combined) and
  the best HYPE read (-$1,629) but the worst per-trade bleeding on BTC
  (expectancy -$13.24) and combined -$7,604. Slower lines mean later
  fan confirmation and stops that sit further from price.
- **jaw=13:** least-bad combined (-$7,538) and best PF on all three
  coins — but that is an in-sample observation, not a justification.
- **Shipped decision:** keep the canonical 13/8/5 lengths and 8/5/3
  shifts as the registry config regardless. The 13/8/5 setting was
  fixed before any backtest was run — adopted from Bill Williams'
  canonical values, not from the sweep — and being least-bad among
  three negative settings is not evidence the strategy works. No
  parameter rescues this one: every jaw setting is negative on every
  coin, so the honest conclusion is the strategy's, not the parameter's.
