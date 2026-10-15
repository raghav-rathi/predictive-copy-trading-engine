# Ease of Movement — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-20 → 2026-10-15, same costs/sizing). Two smoothing-length
variants against the shipped EMV(14) zero-cross. Throwaway sweep script:
`/tmp/batch6_backtest_all.py` (results in `/tmp/batch6_results.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped EMV14 | BTC | 606 | −$4,984 | −2.93 |
| shipped EMV14 | ETH | 618 | −$5,949 | −3.59 |
| shipped EMV14 | HYPE | 536 | −$1,410 | −0.53 |
| EMV7 (faster) | BTC | 830 | −$7,027 | −5.59 |
| EMV7 (faster) | ETH | 852 | −$5,930 | −3.90 |
| EMV7 (faster) | HYPE | 758 | −$2,938 | −1.56 |
| EMV28 (slower) | BTC | 372 | −$814 | −0.03 |
| EMV28 (slower) | ETH | 412 | −$5,656 | −3.83 |
| EMV28 (slower) | HYPE | 364 | −$630 | −0.12 |

## One-line verdicts

- **EMV7:** 2,440 trades of zero-line chop — the fastest way to donate
  fees in the batch. Dead.
- **EMV28:** cuts BTC's loss to −$814 (Sharpe −0.03, i.e. noise) but
  ETH still craters (−$5,656). Slower doesn't fix a broken concept, it
  just slows the bleeding on one coin.
- **Verdict:** no smoothing length makes EMV positive anywhere. The
  indicator's "ease" read doesn't transfer to 1h crypto. Killed as
  shipped; no variant promoted.
