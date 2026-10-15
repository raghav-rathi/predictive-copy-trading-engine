# McGinley Dynamic — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-20 → 2026-10-15, same costs/sizing). Two speed variants against
the shipped MD(10)/MD(30) cross. Throwaway sweep script:
`/tmp/batch6_backtest_all.py` (results in `/tmp/batch6_results.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped (10,30) | BTC | 86 | +$2,542 | +1.47 |
| shipped (10,30) | ETH | 101 | −$1,173 | −0.52 |
| shipped (10,30) | HYPE | 94 | +$1,271 | +1.13 |
| (5,15) faster | BTC | 198 | −$2,440 | −1.11 |
| (5,15) faster | ETH | 222 | −$1,935 | −0.59 |
| (5,15) faster | HYPE | 184 | +$1,165 | +0.94 |
| (20,60) slower | BTC | 50 | +$3,593 | +2.29 |
| (20,60) slower | ETH | 43 | −$933 | −0.73 |
| (20,60) slower | HYPE | 49 | −$952 | −0.74 |

## One-line verdicts

- **(5,15):** the adaptivity can't save a fast cross — combined
  −$3,209. Even McGinley whipsaws when the periods are this short.
- **(20,60):** the standout variant in the batch — combined +$1,708 on
  just 142 trades, BTC +$3,593 at Sharpe 2.29 (50 trades). But n=50 is
  thin and ETH/HYPE flip negative, so this smells like parameter luck
  until a walk-forward says otherwise.
- **Verdict:** shipped (10,30) stays as the documented config
  (positive combined, honest). The (20,60) variant is flagged for
  walk-forward validation, not promoted — 50 trades is not a finding.
