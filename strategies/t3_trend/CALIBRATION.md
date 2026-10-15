# Tillson T3 — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-20 → 2026-10-15, same costs/sizing). Two period variants against
the shipped T3(5)/T3(15) cross (a=0.7). Throwaway sweep script:
`/tmp/batch6_backtest_all.py` (results in `/tmp/batch6_results.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped (5,15) | BTC | 295 | −$1,490 | −0.41 |
| shipped (5,15) | ETH | 317 | −$2,737 | −1.12 |
| shipped (5,15) | HYPE | 289 | +$2,926 | +1.54 |
| (8,21) slower | BTC | 197 | −$74 | +0.23 |
| (8,21) slower | ETH | 209 | −$1,531 | −0.53 |
| (8,21) slower | HYPE | 206 | +$783 | +0.58 |
| (3,8) faster | BTC | 569 | −$6,680 | −5.08 |
| (3,8) faster | ETH | 574 | −$4,937 | −2.90 |
| (3,8) faster | HYPE | 565 | −$1,509 | −0.65 |

## One-line verdicts

- **(3,8):** 1,708 trades, −$13,126 — the low-lag smoother at low
  periods is just a fast EMA with extra steps. Dead.
- **(8,21):** less bad everywhere (combined −$821, BTC Sharpe +0.23)
  but still negative combined — slower trims the bleed without
  creating edge.
- **Verdict:** shipped (5,15) stays documented; the HYPE print
  (+30.3%, Sharpe 1.54) is the only thing worth remembering, and it is
  coin-scoped. No variant promoted.
