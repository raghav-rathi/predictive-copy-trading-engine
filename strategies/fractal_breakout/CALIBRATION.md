# Fractal Breakout (Bill Williams) — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-19, same costs/sizing). Fractal size `n` = bars on
each side: 1 (3-bar fractals) / 2 (shipped 5-bar) / 3 (7-bar fractals).
Larger n = fewer, more significant structure points, longer confirmation lag.

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| n=2 (shipped) | BTC | 316 | 29.4% | -$3,454 | -3.60 | 0.61 |
| n=2 (shipped) | ETH | 305 | 26.2% | -$2,936 | -2.70 | 0.66 |
| n=2 (shipped) | HYPE | 324 | 30.2% | -$1,562 | -1.68 | 0.80 |
| n=1 | BTC | 396 | 29.3% | -$4,217 | -4.93 | 0.54 |
| n=1 | ETH | 435 | 28.0% | -$4,242 | -4.69 | 0.56 |
| n=1 | HYPE | 451 | 32.8% | -$3,171 | -4.17 | 0.63 |
| n=3 | BTC | 265 | 25.7% | -$3,191 | -3.15 | 0.61 |
| n=3 | ETH | 251 | 30.3% | -$1,459 | -1.12 | 0.81 |
| n=3 | HYPE | 267 | 29.6% | -$570 | -0.42 | 0.93 |

## One-line verdict

- **n=1 (3-bar fractals):** strictly worse everywhere -- more levels,
  more false breakouts, more fee drag (435-451 trades/coin, Sharpe
  -4.17 to -4.93).
- **n=3 (7-bar fractals):** the least-bad setting -- fewer trades, and
  ETH/HYPE losses shrink (-$1,459 / -$570), but every coin stays
  negative and BTC barely improves (-$3,191).
- **Shipped decision:** keep n=2 as specified. The n=3 improvement is
  measured on the same 7-month in-sample window and still loses money
  on all three coins -- adopting it would be in-sample selection on a
  system that is negative in every configuration. The honest conclusion
  stands: fractal breakout, in this form, does not trade 1h crypto
  profitably.
