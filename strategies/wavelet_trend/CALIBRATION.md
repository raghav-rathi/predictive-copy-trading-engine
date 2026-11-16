# Wavelet Trend — Calibration

Level sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-11-16, same costs/sizing, 1.5xATR
stop, 2.5xATR target, 72-bar max hold). The sweep re-runs
`add_indicators(df, levels=L)` only — signals and risk are unchanged.

| Levels | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 2 | BTC | 572 | 23.6% | -$7,128 | -9.58 | 0.40 | -$12.46 |
| 2 | ETH | 576 | 29.9% | -$5,244 | -5.52 | 0.59 | -$9.10 |
| 2 | HYPE | 522 | 32.0% | -$4,921 | -6.01 | 0.54 | -$9.43 |
| 3 (shipped) | BTC | 597 | 23.6% | -$7,211 | -8.97 | 0.43 | -$12.08 |
| 3 (shipped) | ETH | 623 | 26.5% | -$6,488 | -7.19 | 0.50 | -$10.41 |
| 3 (shipped) | HYPE | 572 | 31.6% | -$4,702 | -4.75 | 0.63 | -$8.22 |
| 4 | BTC | 402 | 29.9% | -$5,022 | -4.31 | 0.65 | -$12.49 |
| 4 | ETH | 422 | 29.9% | -$4,047 | -3.08 | 0.76 | -$9.59 |
| 4 | HYPE | 388 | 33.2% | -$1,768 | -1.12 | 0.89 | -$4.56 |

## One-line verdict

- **levels=2:** less denoising, same whipsaw — combined -$17,293,
  statistically indistinguishable from shipped.
- **levels=4:** heavier denoising, fewer turns (388–422 trades per
  coin), combined -$10,837 — the least bad, but still red on all
  three coins with BTC at -$5,022.
- **levels=3 (shipped):** worst combined (-$18,401). The extra
  smoothing of level 4 helps only by trading less, not by trading
  better: win rates stay in the 20s–30s at every level.
- **Shipped decision:** keep the specified levels=3 as the registry
  config regardless. It was fixed before any backtest was run; the
  in-sample ranking (levels=4 loses least) does not change that,
  and leaning toward levels=4 *because* it loses least would be
  in-sample selection on a window where no setting works. The honest
  read: the level moves how much the strategy whipsaws, not whether
  it works — the approximation-slope premise itself fails on 1h
  crypto.
