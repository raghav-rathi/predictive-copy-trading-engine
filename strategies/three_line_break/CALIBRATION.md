# Three-Line Break Turnaround — Calibration

Reference-line-count sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-19, same costs/sizing,
2xATR stop, 60-bar max hold). Fewer reference lines = easier reversals
= in principle more flips; more lines = stricter.

| Lines | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| 3 (shipped) | BTC | 4 | 75.0% | +$319 | +0.77 | 3.92 |
| 3 (shipped) | ETH | 4 | 0.0% | -$417 | -2.98 | 0.00 |
| 3 (shipped) | HYPE | 2 | 50.0% | +$107 | +0.48 | 2.03 |
| 2 | BTC | 4 | 75.0% | +$287 | +0.69 | 3.63 |
| 2 | ETH | 4 | 0.0% | -$417 | -2.98 | 0.00 |
| 2 | HYPE | 2 | 50.0% | +$107 | +0.48 | 2.03 |
| 4 | BTC | 4 | 75.0% | +$287 | +0.69 | 3.63 |
| 4 | ETH | 4 | 0.0% | -$417 | -2.98 | 0.00 |
| 4 | HYPE | 2 | 50.0% | +$107 | +0.48 | 2.03 |

## One-line verdict

- The parameter barely matters: 2/3/4 lines give 4/4/2 trades in all
  three variants; BTC's net moves $319 → $287 on one trade's exit
  price, ETH and HYPE are bit-identical. The flip count is not
  monotone in the line count (path-dependent line ranges), and with
  ~10 signals total no variant is distinguishable from noise.
- The binding constraint is the technique's frequency at the 1h
  timeframe (7 completed lines in 7 months on BTC), not the
  reference-line count. There is no sensitivity worth chasing.
- **Shipped decision:** keep the specified 3-line reference. Nothing
  in this sweep argues for a change, and nothing could — the sample is
  too small to select on.
