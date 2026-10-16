# Ehlers RVI — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-15, same costs/sizing). Two parameters: the
minimum RVI/signal separation at the cross (0 = unfiltered, 0.02,
0.05) and the RVI smoothing length (10 vs 14). Throwaway sweep script:
`/tmp/batch7_calibrate.py` (results in `/tmp/batch7_calib.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped sep0/len10 | BTC | 134 | +$1,232 | +0.89 |
| shipped sep0/len10 | ETH | 137 | −$901 | −0.02 |
| shipped sep0/len10 | HYPE | 148 | −$2,129 | −1.06 |
| sep0/len14 | BTC | 159 | −$1,211 | −0.41 |
| sep0/len14 | ETH | 155 | −$577 | −0.09 |
| sep0/len14 | HYPE | 140 | +$1,649 | +0.93 |
| sep0.02/len10 | BTC | 137 | +$1,333 | +0.94 |
| sep0.02/len10 | ETH | 137 | +$1,091 | +0.92 |
| sep0.02/len10 | HYPE | 138 | −$1,316 | −0.52 |
| sep0.02/len14 | BTC | 138 | −$2,224 | −1.16 |
| sep0.02/len14 | ETH | 134 | −$419 | +0.06 |
| sep0.02/len14 | HYPE | 126 | +$945 | +0.82 |
| sep0.05/len10 | BTC | 124 | −$2,461 | −1.24 |
| sep0.05/len10 | ETH | 128 | −$811 | +0.01 |
| sep0.05/len10 | HYPE | 119 | −$598 | −0.09 |
| sep0.05/len14 | BTC | 103 | +$2,026 | +1.15 |
| sep0.05/len14 | ETH | 114 | −$112 | +0.07 |
| sep0.05/len14 | HYPE | 101 | +$2,718 | +1.57 |

## One-line verdicts

- **The filter is the strategy.** Unfiltered crosses churn: the
  shipped sep0/len10 is −$1,798 combined. Adding the 0.02 separation
  filter flips ETH from −$901 to +$1,091, nudges BTC up, and cuts the
  HYPE loss nearly in half — combined +$1,108. Whipsaw crosses are
  where this system bleeds, and the filter targets exactly those.
- **Length 14 is unstable:** it rescues HYPE unfiltered (+$1,649) but
  wrecks BTC (−$1,211), and the combinations swing wildly. Length 10
  behaves monotonically with the filter — the safer base.
- **sep0.05/len14 (+$4,632 combined) smells of overfit:** the best
  combined print comes from the most restrictive variant on the
  smoothest setting, with ETH contributing nothing (−$112). Two coins
  do not make a robust system.
- **Verdict:** keep the shipped unfiltered config as the documented
  baseline, but the honest recommendation is sep0.02/len10 — positive
  on two of three coins, smallest HYPE draw of the losers, same trade
  count. Promote it pending walk-forward validation; do not touch
  sep0.05/len14 without out-of-sample proof.
