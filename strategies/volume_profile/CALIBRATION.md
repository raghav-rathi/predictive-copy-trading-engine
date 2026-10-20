# Volume Profile Value-Area Fade — Calibration

Value-area coverage sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-20, same costs/sizing,
2xATR stop, 3xATR target, 120-bar max hold). Coverage sets how wide
the value area is: narrower = more failed-auction triggers closer to
the POC; wider = rarer extremes at the fringes.

| VA coverage | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 70% (shipped) | BTC | 95 | 40.0% | -$1,023 | -1.15 | 0.83 | -$10.77 |
| 70% (shipped) | ETH | 79 | 40.5% | -$601 | -0.67 | 0.87 | -$7.61 |
| 70% (shipped) | HYPE | 80 | 36.2% | -$1,345 | -1.52 | 0.74 | -$16.82 |
| 60% | BTC | 94 | 43.6% | -$214 | -0.16 | 0.96 | -$2.27 |
| 60% | ETH | 73 | 41.1% | -$437 | -0.49 | 0.90 | -$5.99 |
| 60% | HYPE | 100 | 35.0% | -$1,750 | -2.05 | 0.72 | -$17.50 |
| 80% | BTC | 91 | 42.9% | -$354 | -0.33 | 0.94 | -$3.90 |
| 80% | ETH | 91 | 41.8% | -$538 | -0.52 | 0.90 | -$5.91 |
| 80% | HYPE | 83 | 39.8% | -$666 | -0.69 | 0.88 | -$8.02 |

## One-line verdict

- **60%:** combined −$2,401 (BTC nearly flat at −$214, PF 0.96) —
  narrower value areas trigger more often but no coin turns positive.
- **80%:** least negative in-sample (combined −$1,558, every coin
  PF ≥ 0.88) — fringe extremes fade slightly better, still red
  everywhere.
- **Shipped decision:** keep the specified 70%. The sweep shows the
  book is roughly cost-dragged to zero at the fringes, but no setting
  is green — adopting 60% or 80% would be in-sample selection. The
  coverage knob is real (wider VA = closer to breakeven here) and
  worth revisiting with walk-forward evidence, not this window.
