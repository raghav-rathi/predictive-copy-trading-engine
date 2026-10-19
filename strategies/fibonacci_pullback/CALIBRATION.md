# Fibonacci Pullback Entry — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-19, same costs/sizing). Swing-detection window:
40 / 60 (shipped) / 90 bars (same SMA200 filter, same signal rules,
same risk).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| swing=60 (shipped) | BTC | 90 | 22.2% | -$482 | -0.15 | 0.94 |
| swing=60 (shipped) | ETH | 98 | 18.4% | +$1,375 | +0.79 | 1.14 |
| swing=60 (shipped) | HYPE | 86 | 23.3% | +$1,830 | +1.13 | 1.22 |
| swing=40 | BTC | 93 | 24.7% | +$3,150 | +1.56 | 1.33 |
| swing=40 | ETH | 96 | 19.8% | +$2,670 | +1.27 | 1.28 |
| swing=40 | HYPE | 81 | 29.6% | +$2,863 | +1.65 | 1.40 |
| swing=90 | BTC | 88 | 19.3% | -$1,574 | -0.89 | 0.81 |
| swing=90 | ETH | 101 | 18.8% | +$930 | +0.58 | 1.10 |
| swing=90 | HYPE | 71 | 31.0% | +$4,544 | +2.36 | 1.70 |

## One-line verdict

- **Swing=40:** beats the shipped window on every coin in-sample --
  BTC flips from -$482 to +$3,150 (Sharpe +1.56), ETH nearly doubles,
  HYPE's Sharpe rises to +1.65. Shorter swing legs refresh faster on 1h
  crypto, so the retracement pockets track the active impulse instead
  of a stale 60-bar extreme.
- **Swing=90:** mixed -- HYPE explodes to +$4,544 (Sharpe +2.36) while
  BTC sinks to -$1,574; wider legs mean fewer, more selective entries,
  and the coin split widens.
- **Shipped decision:** keep the specified 60-bar window. The 40-bar
  window's clean sweep is measured on the same 7-month in-sample window
  used to notice it -- adopting it now would be pure in-sample
  selection. Flag it as the first candidate for a walk-forward /
  out-of-sample check, not as the shipped config.
