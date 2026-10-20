# VPIN Toxicity Exhaustion — Calibration

Percentile-trigger sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-20, same costs/sizing,
2xATR stop, 2xATR target, 48-bar max hold). The trigger is the rarity
knob: lower = more panic-fades, more whipsaw; higher = rarer, more
"toxic" extremes.

| Trigger | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 0.90 (shipped) | BTC | 50 | 48.0% | -$833 | -1.35 | 0.70 | -$16.66 |
| 0.90 (shipped) | ETH | 66 | 45.5% | -$1,619 | -2.45 | 0.60 | -$24.53 |
| 0.90 (shipped) | HYPE | 62 | 43.5% | -$1,092 | -1.78 | 0.68 | -$17.62 |
| 0.85 | BTC | 71 | 46.5% | -$1,455 | -2.03 | 0.64 | -$20.49 |
| 0.85 | ETH | 82 | 43.9% | -$2,180 | -2.93 | 0.56 | -$26.58 |
| 0.85 | HYPE | 87 | 44.8% | -$1,302 | -1.85 | 0.72 | -$14.97 |
| 0.95 | BTC | 30 | 46.7% | -$570 | -1.13 | 0.68 | -$18.99 |
| 0.95 | ETH | 41 | 36.6% | -$1,575 | -3.13 | 0.45 | -$38.41 |
| 0.95 | HYPE | 38 | 42.1% | -$772 | -1.54 | 0.64 | -$20.32 |

## One-line verdict

- **0.85:** worst everywhere (combined −$4,937 on 240 trades) — more
  fades, more whipsaw, no payoff for the extra selectivity loss.
- **0.95:** least negative in-sample (combined −$2,917) but on only
  109 trades and still red on all three coins — thin and unadoptable.
- **Shipped decision:** keep the specified 0.90. The sweep moves the
  loss around but never removes it: the fade premise fails on this
  window at every rarity setting. Adopting 0.95 would be in-sample
  selection on a loser — say so plainly and keep the documented
  default.
