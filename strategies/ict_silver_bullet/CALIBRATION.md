# Silver Bullet Killzones (ICT) — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-18, same costs/sizing). One variant against the
shipped config: killzone restricted to 10:00–11:00 NY only (the
highest-volume hour of the three) instead of all three killzones.
Sweep script: `/tmp/bt_batch9.py` (`ict_silver_bullet cal` mode).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped 3 killzones | BTC | 7 | 42.9% | +$40 | +0.18 | 1.08 |
| shipped 3 killzones | ETH | 3 | 0.0% | -$369 | -2.19 | 0.00 |
| shipped 3 killzones | HYPE | 3 | 33.3% | -$50 | -0.18 | 0.78 |
| 10:00 only | BTC | 6 | 33.3% | -$135 | -0.56 | 0.72 |
| 10:00 only | ETH | 3 | 0.0% | -$369 | -2.19 | 0.00 |
| 10:00 only | HYPE | 0 | — | $0 | 0.00 | — |

## One-line verdict

- **10:00–11:00 only:** strictly worse — 9 trades vs 13, combined
  -$504 vs -$379 shipped, and HYPE stops trading entirely. Cutting two
  killzones removes setups without improving the quality of the ones
  that remain; on this sample there is no evidence the 10:00 hour is
  special.
- **Shipped decision:** keep all three specified killzones as the
  registry config. With 13 in-sample trades neither config has an edge;
  the variant only shrinks an already ungradable sample.
