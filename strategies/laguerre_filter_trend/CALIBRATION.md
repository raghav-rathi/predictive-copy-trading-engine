# Laguerre Filter Trend — Calibration

Gamma sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-18, same costs/sizing, 2xATR stop,
3xATR trail, 200-bar max hold). The sweep re-runs
`add_indicators(df, gamma=X)` only — signals and risk are unchanged.

| Gamma | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 0.5 | BTC | 251 | 21.9% | -$3,693 | -4.35 | 0.51 | -$14.71 |
| 0.5 | ETH | 247 | 23.1% | -$1,615 | -1.55 | 0.79 | -$6.54 |
| 0.5 | HYPE | 241 | 27.0% | -$817 | -0.75 | 0.88 | -$3.39 |
| 0.8 (shipped) | BTC | 159 | 20.1% | -$2,005 | -1.94 | 0.66 | -$12.61 |
| 0.8 (shipped) | ETH | 190 | 15.3% | -$3,151 | -4.11 | 0.45 | -$16.58 |
| 0.8 (shipped) | HYPE | 143 | 18.2% | -$1,306 | -1.46 | 0.72 | -$9.13 |
| 0.9 | BTC | 111 | 19.8% | -$1,783 | -2.25 | 0.61 | -$16.06 |
| 0.9 | ETH | 133 | 13.5% | -$2,104 | -2.69 | 0.59 | -$15.82 |
| 0.9 | HYPE | 111 | 22.5% | +$854 | +0.96 | 1.23 | +$7.70 |

## One-line verdict

- **gamma=0.5:** the fastest filter, the most trades (241–251/coin),
  combined -$6,125. More responsiveness just means more whipsaw.
- **gamma=0.9:** the slowest filter, fewest trades (111–133/coin),
  combined -$4,033 — the least bad, and the only setting with a green
  coin (HYPE +$854, Sharpe +0.96). But BTC and ETH are still
  -$1,783 / -$2,104, so slower does not fix the mechanism.
- **gamma=0.8 (shipped):** worst combined (-$6,462) of the three
  settings — an in-sample observation, not a reason to move.
- **Shipped decision:** keep the specified gamma=0.8 as the registry
  config regardless. Gamma=0.8 was fixed before any backtest was run;
  leaning toward gamma=0.9 *because* it is least-bad in-sample would
  be in-sample selection on a strategy that loses at every setting.
  The honest read: no gamma rescues this engine on 1h crypto — the
  price/filter cross itself is the problem, and a trend-strength gate
  or a different exit is needed before retesting.
