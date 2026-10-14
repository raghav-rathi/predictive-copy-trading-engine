# Raschke Anti — calibration

Knob sweep, same data/setup as BACKTEST.md
(BTC/ETH/HYPE 1h, 2026-03-14 → 2026-10-10). Net PnL:

| Variant          | BTC       | ETH       | HYPE      |
|------------------|----------:|----------:|----------:|
| sc=1, aw=5 (default) | -$5,498.25 | -$4,185.93 | -$1,625.11 |
| sc=2, aw=5       | -$3,700.26 | -$1,767.82 | -$2,191.30 |
| sc=1, aw=3       | -$5,101.62 | -$3,520.62 |   -$892.63 |
| sc=1, aw=8       | -$6,772.51 | -$5,037.21 | -$3,284.06 |

## Decision

Ship the published-style defaults (slope_confirm=1, arm_window=5).
slope_confirm=2 loses less on BTC/ETH but loses MORE on HYPE; it is
not stable across all three coins, so it is not adopted. arm_window=3
loses less on all three coins than 5, but the strategy is a decisive
loser at every setting — picking the least-bad parameter of a failed
strategy is overfitting, not calibration. Defaults shipped as the
published method describes; see BACKTEST.md for the honest result.
