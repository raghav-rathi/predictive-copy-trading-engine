# DPO Zero-Line Cross — Calibration

Length sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same costs/sizing, 2xATR stop,
2.5xATR trail, 150-bar max hold). The sweep re-runs
`add_indicators(df, n=X)` only — signals (with the SMA(50) trend
filter) and risk are unchanged.

**n=20 was fixed a priori as the shipped setting — before any backtest
was run. The sweep exists only to document sensitivity, not to select
the length.**

| Length | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 314 | 25.8% | -$3,398 | -2.68 | 0.68 | -$10.82 |
| 10 | ETH | 349 | 26.4% | -$2,134 | -1.38 | 0.82 | -$6.11 |
| 10 | HYPE | 282 | 24.5% | -$2,234 | -2.04 | 0.74 | -$7.92 |
| 20 (shipped) | BTC | 243 | 23.5% | -$3,229 | -2.79 | 0.63 | -$13.29 |
| 20 (shipped) | ETH | 271 | 25.5% | -$1,343 | -0.98 | 0.87 | -$4.96 |
| 20 (shipped) | HYPE | 243 | 23.5% | -$166 | -0.02 | 0.98 | -$0.68 |
| 30 | BTC | 265 | 26.0% | -$2,358 | -1.91 | 0.75 | -$8.90 |
| 30 | ETH | 300 | 24.0% | -$2,180 | -1.72 | 0.80 | -$7.27 |
| 30 | HYPE | 259 | 27.0% | +$1,238 | +0.94 | 1.13 | +$4.78 |

## One-line verdict

- **n=10:** the chop setting — 945 trades, -$7,766 combined, every
  coin deeply red (BTC -$3,398, PF 0.68). A fast DPO just re-loses
  the same cycle turn over and over.
- **n=20 (shipped):** worst combined of the three (-$4,738, PF 0.83)
  — BTC (-$3,229) and ETH (-$1,343) both bleed, HYPE (-$166) is a
  coin flip. The shipped length is red on every coin; that is
  reported, not rationalized.
- **n=30:** the least-bad (-$3,300 combined) and the only setting
  with any green coin — HYPE +$1,238 (Sharpe +0.94, PF 1.13) — but
  BTC and ETH still lose $2.3–2.2k each.
- **Shipped decision:** n=20 stays, fixed before the first run.
  Switching to n=30 because it reads best in-sample would be exactly
  the selection bias the honest-loser standard exists to prevent.
  The sweep's real message: the length moves which coin bleeds less,
  not whether the strategy works — a trend-filtered zero-cross on
  1h crypto does not clear costs in this window at any setting.
