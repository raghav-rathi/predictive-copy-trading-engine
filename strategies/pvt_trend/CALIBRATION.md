# Price-Volume Trend — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-20 → 2026-10-15, same costs/sizing). Two MA-length variants
against the shipped PVT/MA20 cross. Throwaway sweep script:
`/tmp/batch6_backtest_all.py` (results in `/tmp/batch6_results.json`;
indicators/risk unchanged).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped MA20 | BTC | 421 | −$3,443 | −1.55 |
| shipped MA20 | ETH | 447 | −$4,638 | −2.34 |
| shipped MA20 | HYPE | 374 | +$1,672 | +1.02 |
| MA10 (faster) | BTC | 728 | −$6,981 | −5.13 |
| MA10 (faster) | ETH | 707 | −$6,659 | −4.47 |
| MA10 (faster) | HYPE | 698 | −$2,954 | −1.63 |
| MA40 (slower) | BTC | 272 | −$3,472 | −1.73 |
| MA40 (slower) | ETH | 222 | −$1,486 | −0.34 |
| MA40 (slower) | HYPE | 228 | +$3,823 | +1.90 |

## One-line verdicts

- **MA10:** doubles the trade count (2,133) and more than doubles the
  loss — the pressure cross at 10 bars is pure noise. Dead.
- **MA40:** the only direction that helps — halves churn, lifts HYPE
  to Sharpe 1.90, cuts the majors' losses. But BTC/ETH stay negative,
  so slower only trims the bleed; it doesn't create edge on chop.
- **Shipped MA20 stays** as the documented middle, with the note that
  any future work on PVT starts at MA40+, not below.
