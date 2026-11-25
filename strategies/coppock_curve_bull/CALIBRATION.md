# Coppock Curve Bull — Calibration

WMA-window sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-46 window
2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC, 6,136 bars
BTC/ETH, 6,134 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 240-bar max hold). WMA window is the strategy's natural
knob: how much smoothing the ROC sum gets — 120 is twitchier
(more hooks), 480 is slower (fewer, later hooks). The sweep
re-runs `add_indicators(df, wma_window=X)` only — signals and
risk are unchanged.

| WMA window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 120 | BTC | 147 | 19.7% | -$2,236 | -2.10 | 0.59 | -$15.21 |
| 120 | ETH | 121 | 26.4% | -$2,046 | -2.49 | 0.53 | -$16.91 |
| 120 | HYPE | 147 | 26.5% | -$244 | -0.17 | 0.96 | -$1.66 |
| 240 (shipped) | BTC | 95 | 21.1% | -$1,021 | -0.94 | 0.76 | -$10.75 |
| 240 (shipped) | ETH | 87 | 26.4% | -$853 | -0.95 | 0.77 | -$9.81 |
| 240 (shipped) | HYPE | 80 | 30.0% | +$163 | +0.26 | 1.05 | +$2.03 |
| 480 | BTC | 72 | 18.1% | -$1,854 | -2.92 | 0.38 | -$25.75 |
| 480 | ETH | 73 | 24.7% | -$1,318 | -1.97 | 0.49 | -$18.05 |
| 480 | HYPE | 73 | 31.5% | -$218 | -0.27 | 0.91 | -$2.99 |

## One-line verdict

- **120:** the worst read (-$4,526 combined, 415 trades) — less
  smoothing means the curve hooks on every 5-day wiggle.
- **240:** the shipped setting and the least negative combined
  (-$1,712, 262 trades) — HYPE positive (+$163, PF 1.05), BTC
  and ETH negative.
- **480:** in between (-$3,390 combined, 218 trades) — slower
  hooks, but BTC expectancy collapses to -$25.75/trade; the
  knob is not monotone (120 → -$4,526, 240 → -$1,712,
  480 → -$3,390).
- **Shipped decision:** keep the specified WMA window 240 as
  the registry config regardless. It was fixed before any
  backtest was run; the sweep's "least negative" is not an
  edge, and adopting 240 *because* it is least negative
  in-sample would be in-sample selection. The honest read:
  the Coppock hook has no edge on 1h bars at any smoothing
  width. Do not ship a different window on the strength of
  this sweep.

## Batch-46 audit (2026-11-25)

- **Lookahead audit:** no lookahead found. ROC uses closes up
  to bar i only (shift(336)/shift(264)); the WMA is a causal
  rolling window ending at bar i with front weights on the
  newest bar; turns compare bars i, i−1, i−2 only; zero crosses
  use `crossed_above`/`crossed_below` on bars i and i−1 only.
  The truncation test (`test_no_lookahead_truncation`) confirms
  indicator and signal values at bar j are identical whether
  computed on the full frame or on the frame truncated at j.
  One real bug was caught and fixed during testing: the WMA
  weights were initially applied backwards (highest weight on
  the oldest bar); the front-weighting is now newest-first,
  verified by a hand-computed test
  (`test_wma_front_weighted`).
- **Source check:** the Wikipedia Coppock Curve article (URL
  given in the batch-46 brief) documents the monthly
  WMA(ROC(14)+ROC(11), 10) formula and the Barron's Oct 15,
  1962 origin; the 336h/264h/240h translation is the documented
  24h/day adaptation, not the monthly original — the README
  says so explicitly. No unscaled 14/11/10-bar parameters are
  used anywhere.
- **Tests:** 12/12 pass (`python3 -m unittest
  strategies.coppock_curve_bull.test_coppock_curve_bull`).
- **No parameter was tuned to PnL.** WMA window stays 240.
