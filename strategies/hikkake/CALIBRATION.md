# Hikkake False-Breakout — Calibration

Confirmation-window sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-20, same costs/sizing,
1.5xATR stop, 3.0xATR target, 20-bar max hold). The window is how many
bars (including the trap bar) a close has to confirm back through the
inside bar's range before the trap expires.

| Window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 3 (shipped) | BTC | 140 | 35.0% | -$2,311 | -2.10 | 0.72 | -$16.51 |
| 3 (shipped) | ETH | 134 | 36.6% | -$1,715 | -1.46 | 0.79 | -$12.80 |
| 3 (shipped) | HYPE | 90 | 37.8% | -$341 | -0.31 | 0.94 | -$3.79 |
| 2 | BTC | 81 | 38.3% | -$459 | -0.42 | 0.91 | -$5.66 |
| 2 | ETH | 63 | 39.7% | -$219 | -0.20 | 0.94 | -$3.47 |
| 2 | HYPE | 48 | 47.9% | +$823 | +1.20 | 1.31 | +$17.14 |
| 4 | BTC | 173 | 36.4% | -$2,108 | -1.69 | 0.79 | -$12.18 |
| 4 | ETH | 191 | 35.6% | -$2,085 | -1.56 | 0.82 | -$10.92 |
| 4 | HYPE | 125 | 37.6% | -$510 | -0.41 | 0.93 | -$4.08 |

## One-line verdict

- **2 bars:** combined +$145 on 192 trades — the only positive setting,
  driven by HYPE (+$823, PF 1.31, Sharpe +1.20). Faster confirmation
  means fresher traps; the edge, such as it is, decays within a bar or
  two.
- **4 bars:** combined -$4,703 on 489 trades — the worst setting. More
  time lets more stale traps confirm into chop; trade count balloons
  and expectancy sinks.
- **Shipped decision:** keep the specified 3-bar window. The 2-bar
  setting beats it in-sample on this exact window, so adopting it now
  would be pure in-sample selection. The honest read: confirmation
  speed is a genuine sensitivity knob (faster = better here), and the
  right choice needs walk-forward or out-of-sample evidence.
