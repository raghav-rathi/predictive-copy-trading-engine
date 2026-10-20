# Kalman Filter Trend — Calibration

Measurement-noise (R = r) sensitivity on the same Hyperliquid 1h data
as BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-20, same
costs/sizing, 2xATR stop, 200-bar max hold). R is the filter's trust
knob: smaller r trusts each close more (twitchier filter, more
crosses), larger r smooths harder (fewer, later signals).

| r (shipped = 1.0) | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 0.5 | BTC | 1,201 | 27.3% | -$8,268 | -9.89 | 0.54 | -$6.88 |
| 0.5 | ETH | 1,137 | 29.1% | -$6,804 | -6.47 | 0.66 | -$5.98 |
| 0.5 | HYPE | 1,218 | 31.5% | -$6,556 | -7.12 | 0.64 | -$5.38 |
| 1.0 (shipped) | BTC | 1,056 | 26.9% | -$7,472 | -7.92 | 0.59 | -$7.08 |
| 1.0 (shipped) | ETH | 978 | 28.0% | -$6,306 | -5.69 | 0.66 | -$6.45 |
| 1.0 (shipped) | HYPE | 1,068 | 31.1% | -$6,168 | -6.57 | 0.65 | -$5.78 |
| 2.0 | BTC | 904 | 27.2% | -$7,103 | -7.88 | 0.60 | -$7.86 |
| 2.0 | ETH | 893 | 25.8% | -$6,031 | -5.34 | 0.66 | -$6.75 |
| 2.0 | HYPE | 904 | 31.7% | -$4,643 | -3.98 | 0.71 | -$5.14 |

## One-line verdict

- **Every setting loses on every coin.** r=2.0 loses the least
  (combined -$17,777 vs -$21,946 shipped) purely by trading less:
  2,701 trades vs 3,102, so ~$2,400 less in fees. r=0.5 is worst
  (combined -$23,628) — a twitchier filter just manufactures more
  fee-paying whipsaw.
- There is no in-sample winner to adopt: nothing is positive at any r
  on any coin. The knob moves the loss around (fewer trades = slower
  bleed), it does not flip the sign.
- **Shipped decision:** keep the specified r=1.0 as the registry
  config. I did not adopt the in-sample "winner" (r=2.0) — selecting
  the least-bad loser on this exact window would be pure in-sample
  selection, and the honest read is that the mechanism itself, not the
  smoothing, is the problem here.
