# OU Half-Life Z-Score Mean Reversion — Calibration

Z-entry threshold sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-20, same costs/sizing,
2.5xATR stop, no target, 200-bar max hold). The threshold is the
deviation-rarity knob: tighter = more trades at smaller stretches;
wider = fewer, deeper deviations.

| Z entry | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 2.0 (shipped) | BTC | 161 | 42.2% | -$3,484 | -3.30 | 0.60 | -$21.64 |
| 2.0 (shipped) | ETH | 152 | 48.0% | -$1,603 | -1.38 | 0.81 | -$10.55 |
| 2.0 (shipped) | HYPE | 138 | 39.9% | -$3,025 | -3.21 | 0.59 | -$21.92 |
| 1.5 | BTC | 224 | 42.0% | -$4,478 | -4.00 | 0.60 | -$19.99 |
| 1.5 | ETH | 209 | 45.0% | -$3,159 | -2.69 | 0.70 | -$15.11 |
| 1.5 | HYPE | 215 | 43.7% | -$3,745 | -3.47 | 0.63 | -$17.42 |
| 2.5 | BTC | 101 | 44.6% | -$1,552 | -1.59 | 0.73 | -$15.36 |
| 2.5 | ETH | 102 | 51.0% | -$341 | -0.26 | 0.94 | -$3.35 |
| 2.5 | HYPE | 85 | 38.8% | -$1,868 | -2.23 | 0.63 | -$21.97 |

## One-line verdict

- **1.5:** worst everywhere (combined −$11,382 on 648 trades) —
  trading every small stretch just multiplies the bleed.
- **2.5:** least negative in-sample (combined −$3,761; ETH nearly
  flat at −$341, PF 0.94) — deeper deviations revert slightly better,
  but every coin is still red.
- **Shipped decision:** keep the specified 2.0. The sweep confirms the
  mechanism's gradient (rarer stretches lose less) but no threshold
  turns the book positive — adopting 2.5 would be in-sample selection
  on a loser. The honest read: fade-rarity is a real sensitivity knob
  and the premise fails at every setting on this window.
