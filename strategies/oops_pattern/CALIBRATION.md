# Oops Gap Reversion — Calibration

Session-length sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-22, same costs/sizing,
1.5xATR stop, 24-bar max hold). The sweep re-runs
`add_indicators(df, session=X)` + `add_signals(df, session=X)` only —
signals logic and risk are unchanged. Window ms
`[1773446400000, 1792627199000)` for all runs.

| Session | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 12 | BTC | 273 | 30.8% | -$5,655 | -4.22 | 0.60 | -$20.72 |
| 12 | ETH | 243 | 38.3% | -$2,681 | -1.52 | 0.81 | -$11.03 |
| 12 | HYPE | 270 | 43.7% | +$2,990 | +1.43 | 1.16 | +$11.07 |
| 24 (shipped) | BTC | 175 | 33.1% | -$3,501 | -2.42 | 0.67 | -$20.01 |
| 24 (shipped) | ETH | 166 | 39.2% | +$25 | +0.15 | 1.00 | +$0.15 |
| 24 (shipped) | HYPE | 185 | 43.2% | +$6,652 | +2.80 | 1.48 | +$35.96 |
| 48 | BTC | 114 | 33.3% | -$2,125 | -1.67 | 0.70 | -$18.64 |
| 48 | ETH | 107 | 37.4% | -$645 | -0.36 | 0.90 | -$6.03 |
| 48 | HYPE | 121 | 33.9% | -$1,161 | -0.81 | 0.85 | -$9.59 |

## One-line verdict

- **session=12:** the chop setting — 786 trades combined, -$5,346
  combined. Shorter sessions make the "prior day" range twitchy, so
  breakdown-opens fire constantly and mostly keep breaking down
  (BTC -$5,655, Sharpe -4.22). Only HYPE stays green (+$2,990).
- **session=48:** fewer, slower setups (342 trades) but the reclaim
  window is too patient — combined -$3,931, and even HYPE flips red
  (-$1,161, the only setting where it does). A 48-bar "day" lets the
  overreaction become the trend.
- **session=24:** best combined (+$3,176) and the only setting with
  HYPE strongly green — but that is an in-sample observation, not a
  justification.
- **Shipped decision:** keep the specified session=24 as the registry
  config regardless. The session=24 length was fixed before any
  backtest was run (it proxies one trading day on 1h bars); the
  in-sample ranking does not change that, and leaning toward
  session=12 or 48 *because* of these numbers would be in-sample
  selection against a 7-month window where HYPE carried everything
  anyway. The honest read: the session length moves which coin pays,
  not whether the strategy works — that still needs walk-forward or
  out-of-sample evidence.
