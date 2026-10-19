# Laguerre RSI (John Ehlers) — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-19, same costs/sizing). Gamma is the only free
parameter: 0.3 (slower, smoother) / 0.5 (shipped) / 0.7 (faster, noisier).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| gamma=0.5 (shipped) | BTC | 704 | 23.3% | -$6,631 | -4.53 | 0.63 |
| gamma=0.5 (shipped) | ETH | 744 | 24.9% | -$5,785 | -3.54 | 0.68 |
| gamma=0.5 (shipped) | HYPE | 621 | 31.2% | -$1,048 | -0.34 | 0.94 |
| gamma=0.3 | BTC | 929 | 23.1% | -$7,494 | -6.25 | 0.61 |
| gamma=0.3 | ETH | 947 | 25.2% | -$6,540 | -4.43 | 0.67 |
| gamma=0.3 | HYPE | 816 | 32.1% | -$4,116 | -2.51 | 0.81 |
| gamma=0.7 | BTC | 411 | 25.1% | -$4,053 | -2.18 | 0.70 |
| gamma=0.7 | ETH | 445 | 27.9% | -$3,916 | -2.15 | 0.74 |
| gamma=0.7 | HYPE | 375 | 31.5% | +$1,127 | +0.69 | 1.08 |

## One-line verdict

- **Gamma=0.7:** the least-bad setting -- the faster filter flips less
  (411-445 trades vs 700+), so fee drag falls and HYPE even prints
  +$1,127 (Sharpe +0.69). But BTC (-$4,053) and ETH (-$3,916) stay
  deeply negative, so no gamma rescues the system.
- **Gamma=0.3:** strictly worse everywhere -- the slower filter lags,
  flips even more often on whipsaw, and fees compound the damage.
- **Shipped decision:** keep gamma=0.5 as specified. Gamma=0.7's smaller
  loss is measured on the same 7-month in-sample window -- adopting it
  would be in-sample selection on a system that is negative in every
  configuration. The honest conclusion stands: this formulation does
  not trade 1h crypto profitably.
