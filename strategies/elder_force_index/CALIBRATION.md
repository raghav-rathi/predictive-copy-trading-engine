# Elder Force Index — Calibration

Trend-EMA sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same costs/sizing, 2xATR stop,
3xATR trail, 100-bar max hold). The trend gauge is EMA(fi, N): N=9 is
faster (whipsaws more), N=21 is slower (fewer, later regime calls). The
sweep re-runs `add_indicators(df, trend_len=X)` only — signals and risk
are unchanged.

| Trend N | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 9 | BTC | 396 | 26.0% | -$4,811 | -4.08 | 0.58 | -$12.15 |
| 9 | ETH | 388 | 29.4% | -$3,820 | -2.63 | 0.68 | -$9.84 |
| 9 | HYPE | 369 | 32.0% | -$573 | -0.26 | 0.95 | -$1.55 |
| 13 (shipped) | BTC | 363 | 27.0% | -$4,003 | -2.76 | 0.67 | -$11.03 |
| 13 (shipped) | ETH | 358 | 29.3% | -$2,936 | -1.75 | 0.76 | -$8.20 |
| 13 (shipped) | HYPE | 330 | 30.0% | -$1,284 | -0.77 | 0.89 | -$3.89 |
| 21 | BTC | 330 | 26.1% | -$4,763 | -3.47 | 0.59 | -$14.43 |
| 21 | ETH | 315 | 27.3% | -$3,122 | -1.86 | 0.74 | -$9.91 |
| 21 | HYPE | 291 | 29.9% | -$866 | -0.41 | 0.93 | -$2.97 |

## One-line verdict

- **N=9:** worst everywhere combined (-$9,204) — the faster gauge just
  churns harder into chop.
- **N=13:** combined -$8,224, the shipped setting; mid-pack on every
  coin, nothing redeeming.
- **N=21:** combined -$8,750 and least-bad on HYPE (-$866) — but the
  shipped N=13 is the least-bad *combined* (-$8,224), and "least
  negative" on a uniformly negative sweep is not an argument for
  anything.
- **Shipped decision:** keep the specified trend length 13 as the
  registry config regardless. It was fixed before any backtest was run,
  and no setting in this sweep turns the strategy positive — changing
  the parameter cannot rescue a trigger with no edge, so there is
  nothing to adopt in-sample.
