# Minervini Trend Template — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-15, same costs/sizing). Two template-selectivity
knobs: the 52wk-low multiple (1.15 vs 1.30) and the within-high multiple
(0.60 vs 0.75). Throwaway sweep script: `/tmp/batch7_calib_b.py`
(results in `/tmp/batch7_calib_b.json`).

| Variant | BTC trades | ETH trades | HYPE trades / net $ |
|---|---|---|---|
| shipped lo1.30_hi0.75 | 0 | 0 | 7 / −$514 |
| lo1.15_hi0.75 | 0 | 0 | 7 / −$514 |
| lo1.30_hi0.60 | 0 | 0 | 7 / −$514 |
| lo1.15_hi0.60 | 0 | 0 | 7 / −$514 |

## One-line verdicts

- **The knobs change nothing.** All four variants produce byte-identical
  results: the binding constraints are the SMA-alignment terms and the
  258-bar tradeable window, not the 52wk multiples. Loosening the
  template does not create a single additional BTC/ETH entry.
- **Shipped config stands by default** (the published 1.30 / 0.75
  values), but honestly the template is unjudgeable here: 7 trades is
  noise, and any "win" would be sample-size suspect.
- **The real calibration is the data, not the parameters.** This
  strategy needs multi-year daily history before any parameter means
  anything. On hourly crypto bars it stays a scaffold.
