# Williams Alligator + Fractal — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-18, same costs/sizing). One variant against the shipped
config. Throwaway sweep script: `/tmp/bt_batch9_sweep.py` (ephemeral;
indicators/risk unchanged).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped stop 1.5xATR | BTC | 152 | 27.6% | -$2,653 | -1.48 | 0.72 |
| shipped stop 1.5xATR | ETH | 168 | 24.4% | -$1,840 | -0.67 | 0.83 |
| shipped stop 1.5xATR | HYPE | 166 | 27.7% | -$1,779 | -0.89 | 0.83 |
| stop 2.0xATR | BTC | 138 | 33.3% | -$589 | -0.29 | 0.91 |
| stop 2.0xATR | ETH | 155 | 26.5% | -$1,592 | -0.81 | 0.82 |
| stop 2.0xATR | HYPE | 157 | 30.6% | -$1,667 | -1.14 | 0.80 |

## One-line verdict

- **Stop 2.0xATR:** wider stops lift BTC to near-breakeven (−$589, PF 0.91,
  win rate 33.3%) — the entries are late and need room — but ETH (−$1,592)
  and HYPE (−$1,667) stay firmly negative. One coin improving while two
  don't, on a single in-sample window, is the classic overfit signature;
  it does not rescue the strategy.
- **Shipped decision:** keep the specified 1.5xATR stop as the registry
  config; the sweep is diagnostic, not an adoption. The strategy is a reject
  either way.
