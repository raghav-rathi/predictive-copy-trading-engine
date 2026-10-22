# Accelerator Oscillator — Calibration

Slow-leg sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, window ms `[1773446400000, 1792627199000)`, same
costs/sizing, 2xATR stop, 2.5xATR trail, 120-bar max hold). The sweep
re-runs `add_indicators(df, fast=5, slow=X, signal=5)` only — signals
and risk are unchanged.

**The shipped config (5, 34, 5) was fixed A PRIORI — Williams'
original published parameters, adopted before any backtest was run.
This sweep is a sensitivity check, not a selection exercise.**

| Slow | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 21 | BTC | 1,055 | 30.1% | -$9,262 | -11.26 | 0.41 | -$8.78 |
| 21 | ETH | 1,076 | 31.5% | -$9,008 | -9.56 | 0.49 | -$8.37 |
| 21 | HYPE | 996 | 36.3% | -$7,648 | -6.93 | 0.59 | -$7.68 |
| 34 (shipped) | BTC | 1,054 | 29.7% | -$9,397 | -12.24 | 0.38 | -$8.92 |
| 34 (shipped) | ETH | 1,073 | 30.3% | -$9,105 | -9.93 | 0.45 | -$8.49 |
| 34 (shipped) | HYPE | 986 | 37.2% | -$6,942 | -5.81 | 0.65 | -$7.04 |
| 55 | BTC | 1,047 | 29.5% | -$9,205 | -11.23 | 0.41 | -$8.79 |
| 55 | ETH | 1,063 | 29.6% | -$8,977 | -9.48 | 0.49 | -$8.45 |
| 55 | HYPE | 963 | 37.7% | -$6,960 | -5.80 | 0.65 | -$7.23 |

## One-line verdict

- **slow=21:** the "best" BTC (-$9,262) and ETH (-$9,008) reads — and
  still catastrophic. Trade count barely moves (the color runs
  dominate the timing, not the slow leg).
- **slow=55:** marginally the best HYPE (-$6,960 vs -$6,942 shipped —
  noise) and the worst ETH. Everything stays red by a wide margin.
- **slow=34 (shipped):** sits in the middle of the pack. No setting
  changes the sign anywhere.
- **Shipped decision:** keep (5, 34, 5) regardless. It was fixed before
  the first backtest from Williams' own specification — the sweep
  exists to demonstrate robustness of the *verdict*, not to pick a
  winner. The honest read: the slow length is not the lever; the 2/3-bar
  color-count rule set is a whipsaw machine at 1h resolution, and no
  reasonable slow leg fixes that. Tuning the shipped config on this
  window would be in-sample selection on a strategy that loses at
  every setting.
