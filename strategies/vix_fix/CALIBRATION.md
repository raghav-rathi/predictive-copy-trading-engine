# VIX Fix Fear-Spike Mean Reversion — Calibration

WVF-lookback sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-20, same costs/sizing,
2xATR stop, 24-bar max hold). The lookback sets how far back the
"highest high" fear reference reaches: shorter = more reactive fear
gauge, longer = slower.

| WVF lookback | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 22 (shipped) | BTC | 279 | 52.0% | -$2,429 | -1.98 | 0.79 | -$8.71 |
| 22 (shipped) | ETH | 267 | 52.8% | -$779 | -0.42 | 0.93 | -$2.92 |
| 22 (shipped) | HYPE | 256 | 48.0% | -$2,969 | -2.96 | 0.70 | -$11.60 |
| 14 | BTC | 270 | 47.4% | -$3,067 | -2.68 | 0.73 | -$11.36 |
| 14 | ETH | 266 | 50.4% | -$441 | -0.19 | 0.96 | -$1.66 |
| 14 | HYPE | 277 | 53.4% | -$646 | -0.50 | 0.93 | -$2.33 |
| 30 | BTC | 287 | 45.6% | -$3,927 | -3.46 | 0.67 | -$13.68 |
| 30 | ETH | 291 | 50.9% | -$1,451 | -0.89 | 0.87 | -$4.99 |
| 30 | HYPE | 252 | 49.6% | -$2,492 | -2.41 | 0.75 | -$9.89 |

## One-line verdict

- **14:** least negative combined (-$4,154 vs -$6,178 shipped) —
  a more reactive fear gauge fires closer to the spike and takes
  smaller losses — but still a loser on all three coins.
- **30:** worst everywhere (-$7,870 combined); the slower gauge
  enters fear spikes late and exits midline crosses later.
- **Shipped decision:** keep the specified 22 as the registry config.
  The 14-lookback beats it in-sample on this exact window, so adopting
  it now would be pure in-sample selection — and it is still negative
  everywhere. The honest read: on 1h crypto the fear-spike mean
  reversion fails across the whole sensitivity range; the lookback is
  not the problem.
