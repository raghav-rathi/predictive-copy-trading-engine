# Chaikin VWAP Combo — Calibration

CMF-window sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-46 window
2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC, 6,136 bars
BTC/ETH, 6,134 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 60-bar max hold). CMF window is the strategy's natural
knob: how many bars of money-flow volume the ratio sums over —
10 is twitchier (more zero-crosses), 40 is smoother (fewer).
The sweep re-runs `add_indicators(df, cmf_window=X)` only —
signals and risk are unchanged.

| CMF window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 674 | 24.9% | -$6,866 | -6.66 | 0.50 | -$10.19 |
| 10 | ETH | 644 | 26.7% | -$5,999 | -5.32 | 0.56 | -$9.32 |
| 10 | HYPE | 582 | 30.8% | -$1,531 | -0.91 | 0.90 | -$2.63 |
| 20 (shipped) | BTC | 484 | 25.2% | -$6,704 | -7.84 | 0.39 | -$13.85 |
| 20 (shipped) | ETH | 439 | 28.2% | -$4,250 | -3.56 | 0.60 | -$9.68 |
| 20 (shipped) | HYPE | 427 | 33.3% | -$1,413 | -1.01 | 0.87 | -$3.31 |
| 40 | BTC | 316 | 26.3% | -$3,545 | -3.17 | 0.57 | -$11.22 |
| 40 | ETH | 290 | 26.2% | -$3,805 | -4.02 | 0.52 | -$13.12 |
| 40 | HYPE | 297 | 31.3% | -$813 | -0.68 | 0.88 | -$2.74 |

## One-line verdict

- **10:** the worst read (-$14,395 combined, 1,900 trades) —
  a 10-bar CMF flips on every hourly wiggle and trades the
  noise at $11,000+ in fees.
- **20:** the shipped setting (-$12,368 combined, 1,350
  trades) — BTC the worst coin in the batch (-$6,704,
  Sharpe -7.84).
- **40:** the least negative combined (-$8,163, 903 trades) —
  fewer crosses, less chop, less fees ($6,199) — but still
  deeply negative on every coin (best coin -$813). The knob
  reduces the bleed; it does not find an edge.
- **Shipped decision:** keep the specified CMF window 20 as
  the registry config regardless. It was fixed before any
  backtest was run; adopting 40 *because* it is less negative
  in-sample would be in-sample selection on a knob whose
  "best" value still loses heavily on all three coins. The
  honest read: the CMF zero-cross entry is structurally too
  noisy for 1h crypto at any window length. Do not ship 40
  on the strength of this sweep.

## Batch-46 audit (2026-11-25)

- **Lookahead audit:** no lookahead found. The money flow
  multiplier, money flow volume and CMF are rolling sums of
  bars up to and including the current bar; the session VWAP
  is a within-day cumulative sum (groupby UTC day) ending at
  the current bar; signals use `crossed_above`/`crossed_below`
  on bars i and i−1 only. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j. No
  `base.ichimoku` (and therefore no chikou lookahead) is used
  anywhere in this batch.
- **Source check:** the StockCharts ChartSchool CMF page
  (URL verified via search 2026-11-25; also cited verbatim
  by the TTR CMF reference) documents the three-step formula
  — multiplier, money flow volume, 20-period sum ratio — and
  the 20-period default, exactly as implemented. The VWAP
  confirmation is this strategy's own addition, documented
  as such. No bug found.
- **Tests:** 13/13 pass (`python3 -m unittest
  strategies.chaikin_vwap_combo.test_chaikin_vwap_combo`).
- **No parameter was tuned to PnL.** CMF window stays 20.
