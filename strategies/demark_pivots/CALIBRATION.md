# DeMark Pivots — Calibration

"Day"-length sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-11-16, same
costs/sizing, ~1.5xATR stop, ~3xATR target, 24-bar max hold). The
sweep re-runs `add_indicators(df, day_bars=D)` only — signals and
risk are unchanged.

| Day (bars) | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 12 | BTC | 482 | 33.6% | -$5,540 | -6.46 | 0.50 | -$11.49 |
| 12 | ETH | 458 | 35.6% | -$4,032 | -4.18 | 0.62 | -$8.80 |
| 12 | HYPE | 515 | 37.5% | -$4,788 | -6.07 | 0.56 | -$9.30 |
| 24 (shipped) | BTC | 468 | 30.8% | -$5,776 | -7.31 | 0.43 | -$12.34 |
| 24 (shipped) | ETH | 459 | 36.8% | -$4,354 | -4.88 | 0.59 | -$9.49 |
| 24 (shipped) | HYPE | 493 | 45.8% | -$2,535 | -2.39 | 0.77 | -$5.14 |
| 48 | BTC | 492 | 32.9% | -$6,373 | -8.32 | 0.42 | -$12.95 |
| 48 | ETH | 432 | 35.6% | -$4,083 | -4.42 | 0.59 | -$8.97 |
| 48 | HYPE | 491 | 40.7% | -$4,402 | -5.06 | 0.59 | -$8.97 |

## One-line verdict

- **12:** combined -$14,360. A 12-bar "day" recomputes levels twice
  as often and loses everywhere (Sharpe -4.18 to -6.46).
- **48:** combined -$14,858, the worst of the three — BTC hits
  Sharpe -8.32 and -$6,373. A 48-bar "day" does not rescue the
  levels; it just makes them staler.
- **24 (shipped):** least bad combined (-$12,665) and the only
  setting with a coin above a 40% win rate (HYPE 45.8%) — and that
  is an in-sample observation, not a justification; every setting
  loses on every coin.
- **Shipped decision:** keep the specified 24-bar "day" as the
  registry config regardless. The 24-bar day was fixed before any
  backtest was run; the in-sample ranking does not change that.
  The honest read: the day length moves which coin pays most, not
  whether hourly-recomputed DeMark pivots work — on this window
  they do not, at any length.
