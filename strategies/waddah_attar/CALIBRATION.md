# Waddah Attar Explosion — Calibration

Sensitivity-knob sweep on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-20, same costs/sizing, 2xATR stop,
3xATR trail, 200-bar max hold). Sensitivity scales the histogram, so it
sets how easily momentum clears the dead zone: lower = more selective,
higher = more permissive.

| Sensitivity | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 150 (shipped) | BTC | 236 | 27.1% | -$2,664 | -3.44 | 0.56 | -$11.29 |
| 150 (shipped) | ETH | 236 | 31.8% | -$1,282 | -1.27 | 0.79 | -$5.43 |
| 150 (shipped) | HYPE | 247 | 29.1% | -$1,866 | -2.99 | 0.64 | -$7.56 |
| 100 | BTC | 222 | 27.5% | -$2,319 | -3.00 | 0.59 | -$10.44 |
| 100 | ETH | 222 | 31.5% | -$1,011 | -1.06 | 0.83 | -$4.55 |
| 100 | HYPE | 243 | 28.4% | -$1,943 | -3.20 | 0.62 | -$7.99 |
| 200 | BTC | 238 | 27.7% | -$2,621 | -3.36 | 0.57 | -$11.01 |
| 200 | ETH | 244 | 31.1% | -$1,483 | -1.50 | 0.77 | -$6.08 |
| 200 | HYPE | 247 | 29.1% | -$1,866 | -2.99 | 0.64 | -$7.56 |

## One-line verdict

- **100:** least negative combined (-$5,273 vs -$5,813 shipped) —
  more selective entries skip some marginal bursts — but still
  negative on all three coins.
- **200:** worst combined (-$6,087); a permissive histogram lets
  weak momentum through the dead zone and the explosion-line exit
  can't contain it.
- **Shipped decision:** keep the author's specified 150 as the
  registry config. The 100-sensitivity beats it in-sample on this
  exact window, so adopting it now would be pure in-sample selection —
  and it still loses everywhere. The knob moves the loss around; it
  does not create an edge.
