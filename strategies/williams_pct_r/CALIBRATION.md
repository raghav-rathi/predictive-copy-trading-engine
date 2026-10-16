# williams_pct_r — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-20 → 2026-10-15, same costs/sizing). Two parameters: wait bars
{3, 5, 7} × %R lookback {10, 14}. Runner: `/tmp/batch7_run.py`
(results in `/tmp/batch7_results.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped (wait 5, n 14) | BTC | 217 | −$4,091 | −4.11 |
| shipped (wait 5, n 14) | ETH | 295 | −$4,278 | −3.82 |
| shipped (wait 5, n 14) | HYPE | 378 | −$4,832 | −4.42 |
| wait 3, n 10 | BTC | 253 | −$3,105 | −2.97 |
| wait 3, n 10 | ETH | 344 | −$3,452 | −2.81 |
| wait 3, n 10 | HYPE | 436 | −$5,167 | −4.83 |
| wait 3, n 14 | BTC | 219 | −$4,214 | −4.25 |
| wait 3, n 14 | ETH | 298 | −$4,349 | −3.88 |
| wait 3, n 14 | HYPE | 380 | −$4,865 | −4.46 |
| wait 5, n 10 | BTC | 253 | −$3,125 | −3.00 |
| wait 5, n 10 | ETH | 341 | −$3,442 | −2.81 |
| wait 5, n 10 | HYPE | 431 | −$5,143 | −4.82 |
| wait 7, n 10 | BTC | 252 | −$3,156 | −3.04 |
| wait 7, n 10 | ETH | 340 | −$3,513 | −2.89 |
| wait 7, n 10 | HYPE | 430 | −$5,192 | −4.91 |
| wait 7, n 14 | BTC | 217 | −$4,092 | −4.11 |
| wait 7, n 14 | ETH | 294 | −$4,372 | −3.94 |
| wait 7, n 14 | HYPE | 376 | −$4,831 | −4.43 |

## One-line verdicts

- **n=10 trims BTC/ETH losses but worsens HYPE:** combined loss moves
  −$13,201 → ~−$11,700 (wait 5, n 10) — a shorter lookback unpins %R
  faster, so fewer trades get caught in pinned regimes. Still deep red
  everywhere.
- **Wait length is nearly irrelevant:** wait 3 vs 5 vs 7 changes
  combined results by <5% — the failure is the trigger concept, not the
  delay.
- **Verdict:** no variant is remotely viable; the least-bad (wait 5,
  n 10) still loses ~$11.7k combined. Shipped config keeps the
  published rule (wait 5, n 14) as the documented baseline. Nothing
  promoted — this rule needs a regime filter or a different market.
