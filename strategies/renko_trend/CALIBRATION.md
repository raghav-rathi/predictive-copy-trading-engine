# Renko Trend — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-20 → 2026-10-15, same costs/sizing). Two brick-size variants
against the shipped 0.5xATR bricks. Throwaway sweep script:
`/tmp/batch6_backtest_all.py` (results in `/tmp/batch6_results.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped 0.5xATR | BTC | 860 | −$7,864 | −7.44 |
| shipped 0.5xATR | ETH | 800 | −$5,602 | −3.59 |
| shipped 0.5xATR | HYPE | 911 | −$6,196 | −4.90 |
| 0.25xATR | BTC | 1,472 | −$8,974 | −11.08 |
| 0.25xATR | ETH | 1,438 | −$8,226 | −8.08 |
| 0.25xATR | HYPE | 1,581 | −$8,197 | −8.95 |
| 1.0xATR | BTC | 373 | −$3,651 | −1.90 |
| 1.0xATR | ETH | 374 | −$2,307 | −0.83 |
| 1.0xATR | HYPE | 375 | +$172 | +0.28 |

## One-line verdicts

- **0.25xATR:** 4,491 trades, −$25,397 combined, Sharpe −11.08 on BTC —
  the single worst configuration in the batch. Smaller bricks just
  print more reversals.
- **1.0xATR:** cuts churn to 1,122 trades and the loss to −$5,786, but
  stays negative everywhere (HYPE +$172 is noise). Bigger bricks mean
  slower bleeding, not edge.
- **Verdict:** the brick-reversal system is structurally wrong for 1h
  perps — the noise is the brick size. Killed as shipped; no variant
  promoted.
