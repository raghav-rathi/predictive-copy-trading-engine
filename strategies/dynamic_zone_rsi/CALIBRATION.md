# Dynamic Zones RSI — Calibration

Percentile sensitivity and Bollinger-variant comparison on the same
Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 →
2026-10-18, same costs/sizing, 2xATR stop, 3xATR trail, 120-bar max
hold). The percentile sweep re-runs `add_indicators(df, buy_pct=X,
sell_pct=Y)` only — signals and risk are unchanged. The Bollinger
variant swaps the zone columns for the RSI Bollinger bands (mean ±
0.8σ over 20 bars) and reuses the same signal logic.

## Percentile pairs

| Zones | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10/90 | BTC | 320 | 36.9% | -$5,154 | -5.21 | 0.56 | -$16.11 |
| 10/90 | ETH | 290 | 37.9% | -$3,941 | -3.51 | 0.65 | -$13.59 |
| 10/90 | HYPE | 297 | 41.8% | -$3,098 | -2.75 | 0.74 | -$10.43 |
| 12/88 (shipped) | BTC | 342 | 35.1% | -$5,623 | -5.90 | 0.52 | -$16.44 |
| 12/88 (shipped) | ETH | 318 | 39.0% | -$3,875 | -3.34 | 0.69 | -$12.19 |
| 12/88 (shipped) | HYPE | 312 | 43.6% | -$3,017 | -2.61 | 0.75 | -$9.67 |
| 20/80 | BTC | 380 | 38.7% | -$5,702 | -6.14 | 0.54 | -$15.01 |
| 20/80 | ETH | 361 | 39.9% | -$3,812 | -3.28 | 0.71 | -$10.56 |
| 20/80 | HYPE | 338 | 47.9% | -$1,480 | -1.17 | 0.87 | -$4.38 |

Combined: 10/90 -$12,192 (907 trades), 12/88 -$12,515 (972),
20/80 -$10,994 (1,079).

## Bollinger variant (RSI mean ± 0.8σ, 20 bars, as zones)

| Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|
| BTC | 557 | 43.3% | -$6,967 | -8.22 | 0.49 | -$12.51 |
| ETH | 566 | 44.9% | -$4,907 | -4.46 | 0.69 | -$8.67 |
| HYPE | 541 | 47.5% | -$4,379 | -4.37 | 0.69 | -$8.09 |

Combined -$16,253 (1,664 trades) — worse than the shipped
percentile version on every coin, with ~70% more trades. The
Bollinger bands hug RSI more tightly than the percentile zones, so
they fire far more often and mostly into noise.

## One-line verdict

- **10/90:** marginally less bad than shipped (-$12,192 vs
  -$12,515) but negative on all three coins; narrower zones, fewer
  trades, same story.
- **20/80:** the least bad combined (-$10,994) and the best HYPE
  read (-$1,480, PF 0.87) — wider zones catch more bounces — but
  still negative on all three coins, and BTC is no better.
- **Bollinger variant:** worse everywhere, more trades, more fees.
  The percentile construction is the right one to ship.
- **Shipped decision:** keep the specified 12/88 percentiles as the
  registry config regardless. The 12/88 pair was fixed a priori from
  the original paper (and the TradingView reference's "88% of the
  sample" both sides); the sweep shows no percentile pair turns
  this positive, so leaning toward 20/80 *because* it loses least
  would be in-sample selection on a losing system. The honest read:
  the percentile choice moves the size of the loss, not its sign.
