# QQE — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-20 → 2026-10-15, same costs/sizing). Two QQE-factor variants
against the shipped 4.236 (Glaz's classic). Throwaway sweep script:
`/tmp/batch6_backtest_all.py` (results in `/tmp/batch6_results.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped 4.236 | BTC | 301 | −$4,111 | −2.46 |
| shipped 4.236 | ETH | 345 | −$3,728 | −1.95 |
| shipped 4.236 | HYPE | 327 | +$5,922 | +2.48 |
| factor 3.0 | BTC | 391 | −$5,887 | −4.20 |
| factor 3.0 | ETH | 401 | −$2,419 | −1.03 |
| factor 3.0 | HYPE | 402 | +$2,895 | +1.36 |
| factor 6.0 | BTC | 251 | −$3,163 | −1.69 |
| factor 6.0 | ETH | 275 | −$2,216 | −1.00 |
| factor 6.0 | HYPE | 264 | +$1,741 | +0.98 |

## One-line verdicts

- **Factor 3.0:** tighter bands = more crosses = worse everywhere
  (combined −$5,411). The trailing levels need room to breathe.
- **Factor 6.0:** wider bands cut churn (790 trades) and trim the
  majors' losses, but HYPE's print collapses to +$1,741 — the edge on
  HYPE lives in the band width, and 6.0 is too wide to catch the legs.
- **Verdict:** the classic 4.236 is the best of the three on every
  coin that matters. Shipped config stands; no variant promoted. The
  open question is coin scope (HYPE-only), not the factor.
