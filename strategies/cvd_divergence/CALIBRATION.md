# CVD Divergence — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-19, same costs/sizing). One parameter varied
against the shipped config: the price-pivot window (shipped 10 →
5 / 20). Divergence lookback 60, 3xATR trailing, exits unchanged.

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| pivot 10 (shipped) | BTC | 262 | 42.4% | -$2,501 | -3.53 | 0.64 |
| pivot 10 (shipped) | ETH | 261 | 43.7% | -$1,713 | -2.21 | 0.76 |
| pivot 10 (shipped) | HYPE | 240 | 44.2% | -$862 | -1.18 | 0.86 |
| pivot 5 | BTC | 339 | 49.6% | -$1,771 | -2.24 | 0.78 |
| pivot 5 | ETH | 337 | 47.5% | -$2,452 | -3.17 | 0.70 |
| pivot 5 | HYPE | 323 | 47.4% | -$1,580 | -2.17 | 0.79 |
| pivot 20 | BTC | 206 | 37.4% | -$1,939 | -2.82 | 0.68 |
| pivot 20 | ETH | 208 | 37.0% | -$855 | -1.05 | 0.87 |
| pivot 20 | HYPE | 185 | 38.9% | -$511 | -0.71 | 0.90 |

## One-line verdict

- **Pivot 5:** more pivots, higher win rates (49.6% BTC) but still
  negative everywhere — finer pivots just find more noise to diverge
  on.
- **Pivot 20:** fewer, more meaningful swing pivots; the loss shrinks
  on every coin (BTC -$1,939, ETH -$855, HYPE -$511) but nothing
  crosses breakeven. Directionally the sweep says "bigger pivots are
  less bad", which is consistent with the BACKTEST.md diagnosis that
  consecutive-bar pivots in straight legs cause re-entry spam.
- **Shipped decision:** keep pivot 10 as specified. The pivot-20
  improvement is monotonic in-sample and tempting, but adopting it on
  this same window would be in-sample selection; it also does not
  turn any coin profitable. A minimum-separation rule between compared
  pivots is the more principled fix to test out-of-sample.
