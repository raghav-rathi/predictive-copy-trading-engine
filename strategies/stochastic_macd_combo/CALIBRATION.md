# Stochastic + MACD Combo — Calibration

%K-period sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-46 window
2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC, 6,136 bars
BTC/ETH, 6,134 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 60-bar max hold). The %K period is the strategy's
natural knob: how far back the Stochastic range looks — 7
reacts fast (more crosses, noisier extremes), 21 reacts
slow (fewer crosses, stickier extremes). The sweep re-runs
`add_indicators(df, k_period=X)` only — signals and risk
are unchanged.

| %K | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 7 | BTC | 41 | 24.4% | -$651 | -2.12 | 0.49 | -$15.87 |
| 7 | ETH | 39 | 30.8% | -$677 | -2.40 | 0.38 | -$17.35 |
| 7 | HYPE | 46 | 32.6% | +$18 | +0.08 | 1.02 | +$0.38 |
| 14 (shipped) | BTC | 24 | 41.7% | -$304 | -1.28 | 0.62 | -$12.65 |
| 14 (shipped) | ETH | 26 | 30.8% | -$606 | -2.33 | 0.32 | -$23.30 |
| 14 (shipped) | HYPE | 23 | 21.7% | -$609 | -2.26 | 0.34 | -$26.47 |
| 21 | BTC | 65 | 30.8% | -$1,066 | -2.07 | 0.50 | -$16.41 |
| 21 | ETH | 61 | 32.8% | -$646 | -1.26 | 0.63 | -$10.59 |
| 21 | HYPE | 72 | 36.1% | -$844 | -2.14 | 0.60 | -$11.73 |

## One-line verdict

- **7:** the least bad combined read (-$1,310, 126 trades)
  and the only positive single-coin cell in the sweep
  (HYPE +$18, PF 1.02) — but that is $18 on 46 trades,
  i.e. noise, and BTC/ETH still lose $651/$677.
- **14:** the shipped setting — combined -$1,518, 73 trades,
  PF 0.42. The fewest trades and the worst combined profit
  factor: the strictest filter, the worst fills.
- **21:** the worst combined read (-$2,557, 198 trades) —
  a longer %K lookback fires more often (the range is wider
  so %K sits at the extremes more) and every extra trade
  loses.
- **Shipped decision:** keep the specified %K period 14 as
  the registry config regardless. It was fixed before any
  backtest was run; adopting 7 *because* it loses least
  in-sample would be in-sample selection on a knob whose
  effect is not monotone (7 → -$1,310, 14 → -$1,518,
  21 → -$2,557) and whose best cell is an $18 breakeven.
  The honest read: no %K lookback fixes a filter that
  requires two disagreeing indicators to agree. Do not
  ship 7 on the strength of this sweep.

## Batch-46 audit (2026-11-25)

- **Lookahead audit:** no lookahead found. %K/%D are
  rolling extremes and a causal SMA through bar j; the
  MACD histogram is causal EMAs through bar j; signals use
  `crossed_above`/`crossed_below` on bars i and i−1 only,
  plus the current bar's %K level and histogram sign. The
  truncation test (`test_no_lookahead_truncation`) confirms
  indicator and signal values at bar j are identical
  whether computed on the full frame or on the frame
  truncated at j.
- **Source check:** the StockCharts ChartSchool Stochastic
  article (verified via search 2026-11-25) defines %K as
  100 × (close − lowest low) / (highest high − lowest low)
  over 14 periods and %D as a 3-period SMA of %K — exactly
  as implemented. MACD(12,26,9) matches `base.macd`.
  No bug found.
- **Tests:** 14/14 pass (`python3 -m unittest
  strategies.stochastic_macd_combo.test_stochastic_macd_combo`).
- **No parameter was tuned to PnL.** %K period stays 14.
