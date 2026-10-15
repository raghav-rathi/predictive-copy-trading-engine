# Chaikin Oscillator — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-20 → 2026-10-15, same costs/sizing). Two EMA-pair variants
against the shipped CHO(3,10) zero-cross. Throwaway sweep script:
`/tmp/batch6_backtest_all.py` (results in `/tmp/batch6_results.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped (3,10) | BTC | 616 | −$6,649 | −3.70 |
| shipped (3,10) | ETH | 652 | −$7,075 | −4.46 |
| shipped (3,10) | HYPE | 530 | −$2,332 | −0.86 |
| (6,21) slower | BTC | 298 | −$5,972 | −3.39 |
| (6,21) slower | ETH | 281 | −$3,018 | −1.28 |
| (6,21) slower | HYPE | 270 | −$1,266 | −0.40 |
| (2,6) faster | BTC | 1,006 | −$9,307 | −9.68 |
| (2,6) faster | ETH | 962 | −$8,449 | −6.40 |
| (2,6) faster | HYPE | 864 | −$4,911 | −2.43 |

## One-line verdicts

- **(2,6):** 2,832 trades, −$22,667 combined, Sharpe −9.68 on BTC —
  the single worst parameter set in the batch. Speed kills.
- **(6,21):** halves churn and trims every coin's loss, but stays
  negative everywhere (best: HYPE −$1,266). Slower only slows the bleed.
- **Verdict:** no EMA pair makes the ADL-momentum cross work on 1h.
  The money-flow signal lives on daily+ accumulation swings. Killed as
  shipped; no variant promoted.
