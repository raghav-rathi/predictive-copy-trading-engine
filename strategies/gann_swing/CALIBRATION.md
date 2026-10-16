# Gann swing — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-15, same costs/sizing). One knob: the main-trend
bar length — 2, 3 (shipped), 4. Throwaway sweep script:
`/tmp/batch7_calib_b.py` (results in `/tmp/batch7_calib_b.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped trend 3 | BTC | 605 | −$7,461 | −7.91 |
| shipped trend 3 | ETH | 584 | −$6,164 | −4.64 |
| shipped trend 3 | HYPE | 544 | −$2,328 | −1.46 |
| trend 2 | BTC | 862 | −$8,534 | −10.88 |
| trend 2 | ETH | 823 | −$6,785 | −5.66 |
| trend 2 | HYPE | 820 | −$5,185 | −4.10 |
| trend 4 | BTC | 480 | −$6,168 | −5.47 |
| trend 4 | ETH | 469 | −$4,422 | −2.75 |
| trend 4 | HYPE | 443 | −$1,899 | −1.15 |

## One-line verdicts

- **Trend 2:** faster flips = 2,505 trades of pure churn, worse on every
  coin. The 1-bar swing already over-trades; a 2-bar main trend just
  joins it.
- **Trend 4:** slower flips cut the trade count ~20% and trim the
  losses, but every coin stays deeply negative (−60%/−42%/−19%). Less
  bad is not good.
- **Verdict:** no variant wins; the shipped 3-bar stands only as the
  documented reference. The strategy is rejected — the pullback-timing
  idea needs a slower timeframe or a stronger trend filter, and that is
  a different strategy, not a parameter.
