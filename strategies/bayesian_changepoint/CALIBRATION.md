# Bayesian Changepoint — Calibration

Hazard sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-11-16, same costs/sizing, 1.5xATR
stop, 72-bar max hold, no target). The sweep re-runs
`add_indicators(df, hazard=h)` only — signals and risk are unchanged.

| Hazard | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 0.005 | BTC | 20 | 15.0% | -$456 | -0.54 | 0.68 | -$22.82 |
| 0.005 | ETH | 24 | 12.5% | -$446 | -0.54 | 0.73 | -$18.60 |
| 0.005 | HYPE | 4 | 50.0% | +$434 | +0.72 | 2.68 | +$108.47 |
| 0.01 (shipped) | BTC | 21 | 19.0% | -$847 | -1.10 | 0.42 | -$40.34 |
| 0.01 (shipped) | ETH | 29 | 13.8% | -$665 | -0.86 | 0.67 | -$22.94 |
| 0.01 (shipped) | HYPE | 5 | 60.0% | +$1,109 | +1.45 | 5.05 | +$221.80 |
| 0.02 | BTC | 25 | 16.0% | -$1,116 | -1.41 | 0.37 | -$44.66 |
| 0.02 | ETH | 35 | 14.3% | -$781 | -0.91 | 0.68 | -$22.32 |
| 0.02 | HYPE | 6 | 66.7% | +$1,285 | +1.73 | 5.60 | +$214.22 |

## One-line verdict

- **hazard=0.005:** fewest trades (48 combined), combined -$469.
  A longer prior mean run length barely changes anything — the
  detector's problem is direction, not frequency.
- **hazard=0.02:** most trades (66 combined), combined -$612.
  More changepoints just means more noisy mean-sign bets.
- **hazard=0.01 (shipped):** combined -$403 — the middle setting,
  and the least bad only because HYPE's 5-trade +$1,109 happens to
  sit here. That HYPE number moves by hundreds of dollars between
  settings on 4–6 trades; it is noise, not signal.
- **Shipped decision:** keep the specified hazard=0.01 as the
  registry config regardless. It was fixed before any backtest was
  run; the in-sample ranking does not change that, and leaning
  toward 0.005 *because* it loses least combined would be
  in-sample selection on 48–66 trades. The honest read: the hazard
  moves how often the strategy bets, not whether the bets pay —
  the post-change mean sign is not a tradeable edge at any hazard.
