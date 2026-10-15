# NVI/PVI — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-20 → 2026-10-15, same costs/sizing). Two EMA-length variants
against the shipped NVI/EMA255 regime cross. Throwaway sweep script:
`/tmp/batch6_backtest_all.py` (results in `/tmp/batch6_results.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped EMA255 | BTC | 79 | −$1,616 | −2.35 |
| shipped EMA255 | ETH | 85 | −$1,240 | −1.47 |
| shipped EMA255 | HYPE | 94 | +$141 | +0.22 |
| EMA100 (faster) | BTC | 137 | −$1,945 | −2.03 |
| EMA100 (faster) | ETH | 102 | −$2,372 | −3.21 |
| EMA100 (faster) | HYPE | 151 | −$205 | −0.03 |
| EMA500 (slower) | BTC | 46 | −$942 | −1.08 |
| EMA500 (slower) | ETH | 45 | −$810 | −1.17 |
| EMA500 (slower) | HYPE | 59 | +$726 | +0.68 |

## One-line verdicts

- **EMA100:** more regime flips, more losses — a 100-bar "smart money
  regime" is just wiggle. Dead.
- **EMA500:** the least-bad variant (combined −$1,026 on 150 trades,
  HYPE +$726 at Sharpe 0.68), but still negative everywhere except a
  thin HYPE print. The pattern is monotonic: slower = less bad, never
  good.
- **Verdict:** Fosback's 255-day regime concept cannot be ported to 1h
  bars by swapping the bar count. Killed as shipped; no variant
  promoted.
