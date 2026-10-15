# Wyckoff Spring/Upthrust — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-20 → 2026-10-15, same costs/sizing). Two range-length variants
against the shipped 50-bar range. Throwaway sweep script:
`/tmp/batch6_backtest_all.py` (results in `/tmp/batch6_results.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped range50 | BTC | 211 | −$4,517 | −2.03 |
| shipped range50 | ETH | 153 | +$2,576 | +1.14 |
| shipped range50 | HYPE | 217 | −$2,935 | −1.24 |
| range30 | BTC | 267 | −$4,981 | −2.41 |
| range30 | ETH | 228 | −$2,724 | −1.11 |
| range30 | HYPE | 289 | −$5,265 | −2.82 |
| range100 | BTC | 128 | −$4,821 | −2.55 |
| range100 | ETH | 90 | +$832 | +0.56 |
| range100 | HYPE | 152 | −$5,779 | −3.68 |

## One-line verdicts

- **Range30:** more ranges = more shakeouts = more breakdowns that
  keep breaking down (combined −$12,969). The 18–24% win rate gets
  worse, not better.
- **Range100:** halves the trade count and keeps ETH positive
  (+$832, Sharpe 0.56), but BTC/HYPE stay deeply negative — a longer
  range doesn't fix a 20% hit rate, it just spaces out the losses.
- **Verdict:** no range length makes springs work on 1h. Wyckoff's
  schematics need multi-week accumulation to mean anything; 30–100 1h
  bars is not a "cause" the law of cause-and-effect can work with.
  Killed as shipped; no variant promoted.
