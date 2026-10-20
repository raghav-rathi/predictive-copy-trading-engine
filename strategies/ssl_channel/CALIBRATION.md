# SSL Channel — Calibration

Channel-length sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-20, same costs/sizing,
2xATR stop, 200-bar max hold). The length is the channel's memory:
shorter = faster flips, more whipsaw; longer = slower, fewer flips.

| Channel len | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 (shipped) | BTC | 432 | 26.2% | -$5,546 | -3.45 | 0.63 | -$12.84 |
| 10 (shipped) | ETH | 434 | 29.7% | -$3,711 | -1.78 | 0.78 | -$8.55 |
| 10 (shipped) | HYPE | 418 | 34.7% | -$827 | -0.26 | 0.95 | -$1.98 |
| 6 | BTC | 602 | 26.1% | -$6,903 | -5.04 | 0.60 | -$11.47 |
| 6 | ETH | 580 | 28.4% | -$4,622 | -2.44 | 0.75 | -$7.97 |
| 6 | HYPE | 560 | 33.8% | -$2,251 | -1.08 | 0.89 | -$4.02 |
| 20 | BTC | 288 | 28.8% | -$2,621 | -1.16 | 0.82 | -$9.10 |
| 20 | ETH | 294 | 24.8% | -$2,988 | -1.37 | 0.81 | -$10.16 |
| 20 | HYPE | 272 | 38.2% | +$2,636 | +1.33 | 1.18 | +$9.69 |

## One-line verdict

- **6:** worst everywhere (-$13,776 combined) — a 6-bar channel flips
  constantly on 1h noise; a whipsaw factory.
- **20:** best combined (-$2,973) and the single bright spot of the
  batch — HYPE +$2,636 (PF 1.18, Sharpe +1.33, 272 trades) — but BTC
  and ETH still lose at every length, so the combined book stays
  negative.
- **Shipped decision:** keep the specified 10 as the registry config.
  The n=20 HYPE print is a single-coin, in-sample bright spot; without
  out-of-sample evidence, adopting it would be cherry-picking. The
  honest read: slower channels whipsaw less, but nothing in the sweep
  turns the BTC/ETH legs positive.
