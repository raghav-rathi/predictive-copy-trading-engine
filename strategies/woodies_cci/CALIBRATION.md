# Woodies CCI — Calibration

Trend-qualifier sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same
costs/sizing, 2xATR stop, 3xATR trail, 60-bar max hold). The
qualifier is the strategy's natural knob: how many consecutive bars
CCI(14) must hold its side of the zero line before a pullback
counts — 4 is loose (more setups, weaker trends), 9 is strict
(fewer setups, stronger trends). The sweep re-runs
`add_signals(df, trend_bars=X)` only — indicators and risk are
unchanged.

| trend_bars | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 4 | BTC | 90 | 23.3% | -$470 | -0.66 | 0.84 | -$5.23 |
| 4 | ETH | 81 | 21.0% | -$753 | -1.14 | 0.73 | -$9.29 |
| 4 | HYPE | 83 | 27.7% | -$439 | -0.62 | 0.85 | -$5.29 |
| 6 (shipped) | BTC | 82 | 20.7% | -$454 | -0.67 | 0.84 | -$5.54 |
| 6 (shipped) | ETH | 75 | 21.3% | -$575 | -0.87 | 0.78 | -$7.67 |
| 6 (shipped) | HYPE | 76 | 28.9% | -$356 | -0.51 | 0.87 | -$4.69 |
| 9 | BTC | 81 | 17.3% | -$905 | -1.48 | 0.67 | -$11.17 |
| 9 | ETH | 69 | 23.2% | -$320 | -0.46 | 0.87 | -$4.63 |
| 9 | HYPE | 70 | 28.6% | -$445 | -0.70 | 0.82 | -$6.36 |

## One-line verdict

- **4:** loosest qualifier, most trades (254) — worst on ETH (-$753,
  PF 0.73) and HYPE (-$439). More setups, same zero edge, more fees.
- **9:** strictest qualifier — worst on BTC (-$905, Sharpe -1.48,
  win rate collapses to 17.3%) and HYPE (-$445); least-bad on ETH
  (-$320) but still firmly negative. Waiting longer for "trend"
  confirmation just means entering later into moves that still
  don't persist.
- **6:** least-bad combined (-$1,385 vs -$1,662 for 4 and -$1,670
  for 9) and best on BTC and HYPE — but that is an in-sample
  observation, not a justification.
- **Shipped decision:** keep the specified trend_bars=6 as the
  registry config regardless. It was fixed before any backtest was
  run; adopting it *because* it is least-bad in-sample would still
  be in-sample selection. The honest read: the qualifier knob is
  nearly flat (combined net spans only -$1,385 to -$1,670 across
  settings, all negative on all coins), which says the problem is
  not how many bars define the trend — it is that CCI>0 persistence
  on 1h crypto does not predict continuation in the first place.
