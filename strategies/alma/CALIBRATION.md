# ALMA Dual Cross — Calibration

Offset sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-20, same costs/sizing, 2xATR stop,
3xATR trail, 200-bar max hold). The offset pulls the Gaussian bell
toward the newest bars: 0.75 is closer to a symmetric Gaussian (more
smoothing, more lag), 0.95 hugs the latest price hardest (least lag,
most jitter). The sweep re-runs `add_indicators(df, offset=X)` only —
signals and risk are unchanged.

| Offset | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 0.75 | BTC | 83 | 30.1% | -$245 | -0.14 | 0.94 | -$2.95 |
| 0.75 | ETH | 77 | 36.4% | +$438 | +0.54 | 1.12 | +$5.68 |
| 0.75 | HYPE | 72 | 37.5% | +$1,095 | +1.02 | 1.33 | +$15.21 |
| 0.85 (shipped) | BTC | 82 | 36.6% | +$1,090 | +1.03 | 1.28 | +$13.29 |
| 0.85 (shipped) | ETH | 80 | 36.3% | +$240 | +0.32 | 1.06 | +$3.00 |
| 0.85 (shipped) | HYPE | 71 | 38.0% | +$856 | +0.83 | 1.26 | +$12.06 |
| 0.95 | BTC | 84 | 35.7% | +$506 | +0.54 | 1.13 | +$6.02 |
| 0.95 | ETH | 79 | 41.8% | +$742 | +0.85 | 1.21 | +$9.39 |
| 0.95 | HYPE | 73 | 34.2% | +$441 | +0.49 | 1.13 | +$6.05 |

## One-line verdict

- **0.75:** best on HYPE (+$1,095, Sharpe +1.02, PF 1.33) and worst on
  BTC (-$245, the only negative coin read in the whole sweep) —
  combined +$1,288. Smoothing helps the fastest coin, costs the
  slowest.
- **0.95:** best on ETH (+$742, Sharpe +0.85) but weakest elsewhere —
  combined +$1,689. The low-lag end helps ETH's choppier 1h
  structure, fades the other two.
- **0.85:** best combined (+$2,186) and the only offset positive on
  all three coins — but that is an in-sample observation, not a
  justification.
- **Shipped decision:** keep the specified offset=0.85 as the
  registry config regardless. The 0.85 offset was fixed before any
  backtest was run; it happens to be the in-sample combined winner
  here, and adopting it *because* of that would still be in-sample
  selection. The honest read: the offset is a mild sensitivity knob
  (per-coin winners split across all three settings: HYPE→0.75,
  ETH→0.95, BTC→0.85), and the right choice needs walk-forward or
  out-of-sample evidence, not this 7-month window.
