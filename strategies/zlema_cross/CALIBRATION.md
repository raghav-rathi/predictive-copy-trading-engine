# Zero-Lag EMA — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-20 → 2026-10-15, same costs/sizing). Two period variants against
the shipped de-lagged ZLEMA(10)/ZLEMA(30) cross. Throwaway sweep script:
`/tmp/batch6_backtest_all.py` (results in `/tmp/batch6_results.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped (10,30) | BTC | 507 | −$6,283 | −4.71 |
| shipped (10,30) | ETH | 494 | −$4,540 | −2.70 |
| shipped (10,30) | HYPE | 469 | +$1,129 | +0.76 |
| (5,15) faster | BTC | 1,016 | −$8,286 | −8.46 |
| (5,15) faster | ETH | 1,009 | −$6,746 | −4.85 |
| (5,15) faster | HYPE | 991 | −$6,170 | −4.72 |
| (20,60) slower | BTC | 207 | −$419 | +0.14 |
| (20,60) slower | ETH | 247 | −$1,861 | −0.65 |
| (20,60) slower | HYPE | 234 | +$3,025 | +1.61 |

## One-line verdicts

- **(5,15):** 3,016 trades, −$21,202 — de-lagging a fast EMA just
  manufactures whipsaw faster. The worst speed in the batch.
- **(20,60):** flips the system positive combined (+$745, HYPE Sharpe
  1.61, BTC flat). De-lagging only pays when the base periods are long
  enough that lag was the actual problem — at (10,30) it isn't.
- **Verdict:** shipped (10,30) stays documented as a loser; the
  (20,60) variant is flagged for walk-forward validation (688 trades
  is a healthier n than McGinley's 142), not promoted.
