# Decycler Trend — Calibration

Cutoff sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, ms
`[1773446400000, 1792627199000)`, same costs/sizing, 2xATR stop,
2xATR trail, 150-bar max hold). The sweep re-runs
`add_indicators(df, period=P)` only — signals and risk are unchanged.

**The cutoff P=20 was fixed a priori — before any backtest was run —
and stays the shipped setting regardless of what this sweep shows.**

| Cutoff P | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 804 | 26.4% | -$7,284 | -9.83 | 0.45 | -$9.06 |
| 10 | ETH | 791 | 26.8% | -$5,854 | -6.29 | 0.59 | -$7.40 |
| 10 | HYPE | 868 | 31.6% | -$4,762 | -5.66 | 0.66 | -$5.49 |
| 20 (shipped) | BTC | 639 | 24.7% | -$6,559 | -7.81 | 0.49 | -$10.26 |
| 20 (shipped) | ETH | 631 | 24.4% | -$4,507 | -3.85 | 0.68 | -$7.14 |
| 20 (shipped) | HYPE | 630 | 29.4% | -$4,382 | -4.48 | 0.62 | -$6.96 |
| 40 | BTC | 448 | 26.3% | -$4,388 | -4.01 | 0.62 | -$9.79 |
| 40 | ETH | 427 | 23.0% | -$3,162 | -2.65 | 0.70 | -$7.40 |
| 40 | HYPE | 444 | 26.8% | -$3,670 | -4.05 | 0.62 | -$8.27 |

## One-line verdict

- **P=10:** the chop setting — 2,463 trades, combined -$17,900,
  Sharpe worse than -5 on every coin. Faster cutoff = the line
  tracks noise, and every cross is a trade.
- **P=40:** the least bad — 1,319 trades, combined -$11,220,
  BTC -$4,388 (vs -$6,559 shipped), ETH -$3,162, HYPE -$3,670.
  A longer cutoff smooths the line enough to cut whipsaws by a
  third, but every coin is still firmly red (best PF is ETH's
  0.70).
- **P=20 (shipped):** combined -$15,448. Not the best, not the
  worst — and that is precisely why it ships.
- **Shipped decision:** keep the specified P=20 regardless. The
  cutoff was fixed a priori; adopting P=40 because it "loses
  less" in-sample would be in-sample selection, and the strategy
  fails at every setting anyway — no cutoff rescues it. The
  honest read: this indicator needs a structural change (a
  smoothing layer on the decycler line itself), not a parameter
  tweak.
