# EMA Ribbon Expansion — Calibration

Compression-window sensitivity on the same Hyperliquid 1h data
as BACKTEST.md (BTC/ETH/HYPE, pinned batch-46 window
2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC, 6,136 bars
BTC/ETH, 6,134 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 60-bar max hold). Compression window is the strategy's
natural knob: how long a lookback the ribbon width must be at
its minimum over — 10 is a hair-trigger coil, 40 demands a
long quiet spell. The sweep re-runs
`add_indicators(df, compression_window=X)` only — signals and
risk are unchanged.

| Compression window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 237 | 22.4% | -$3,939 | -3.48 | 0.54 | -$16.62 |
| 10 | ETH | 240 | 24.6% | -$1,325 | -0.73 | 0.84 | -$5.52 |
| 10 | HYPE | 218 | 25.7% | -$3,391 | -2.67 | 0.57 | -$15.56 |
| 20 (shipped) | BTC | 134 | 22.4% | -$2,358 | -2.59 | 0.51 | -$17.60 |
| 20 (shipped) | ETH | 122 | 27.9% | +$667 | +0.59 | 1.15 | +$5.46 |
| 20 (shipped) | HYPE | 108 | 26.9% | -$917 | -0.76 | 0.80 | -$8.49 |
| 40 | BTC | 47 | 27.7% | -$731 | -1.13 | 0.59 | -$15.56 |
| 40 | ETH | 43 | 25.6% | -$377 | -0.42 | 0.79 | -$8.76 |
| 40 | HYPE | 34 | 29.4% | -$514 | -0.64 | 0.71 | -$15.11 |

## One-line verdict

- **10:** the worst read by far (-$8,655 combined, 695 trades)
  — a 10-bar compression window fires on every minor bunching
  and trades the noise.
- **20:** the shipped setting (-$2,608 combined, 364 trades) —
  ETH positive (+$667, PF 1.15), BTC and HYPE negative.
- **40:** the least negative combined (-$1,622, 124 trades) —
  fewer, more patient entries, but still negative on every coin
  (best coin -$377). The knob reduces the bleed; it does not
  find an edge.
- **Shipped decision:** keep the specified compression window
  20 as the registry config regardless. It was fixed before any
  backtest was run; adopting 40 *because* it is less negative
  in-sample would be in-sample selection on a knob whose
  "best" value still loses on all three coins. The honest read:
  the ribbon-expansion entry has no edge on this window at any
  compression width. Do not ship 40 on the strength of this sweep.

## Batch-46 audit (2026-11-25)

- **Lookahead audit:** no lookahead found. All five EMAs are
  causal `ewm` (adjust=False, min_periods=n); ribbon width,
  compression (rolling 20-bar minimum) and comp_recent
  (rolling 3-bar maximum) read bars up to and including the
  current bar only; alignment compares same-bar EMA values;
  signals use same-bar booleans only. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the GMMA reference (Capital.com, verified
  via search 2026-11-25) documents the two-group 12-EMA
  construction; this strategy is a deliberate variant — a
  single five-EMA ribbon (8/13/21/34/55) with a compression
  gate — distinct from the shipped `guppy_mma`, which averages
  the two six-EMA groups into mean lines. No bug found.
- **Tests:** 13/13 pass (`python3 -m unittest
  strategies.ema_ribbon_cross.test_ema_ribbon_cross`).
- **No parameter was tuned to PnL.** Compression window stays 20.
