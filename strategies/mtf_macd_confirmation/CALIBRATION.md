# Multi-Timeframe MACD Confirmation — Calibration

MACD-parameter sensitivity on the same Hyperliquid 1h data
as BACKTEST.md (BTC/ETH/HYPE, pinned batch-48 window
2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC, 6,184 bars
BTC/ETH, 6,182 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 168-bar max hold). The sweep re-runs
`add_indicators(df, fast=X, slow=Y, signal=9)` with the
signal period held at 9 -- the (fast, slow) pair is the
strategy's natural knob: (8, 17) is a faster, more
responsive MACD, (12, 26) the shipped canonical setting,
(19, 39) a slower, smoother one. The 4h filter uses the same
parameters on the 4h grid.

| MACD | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 8,17,9 (faster) | BTC | 238 | 26.9% | -$2,921 | -2.71 | 0.63 | -$12.28 |
| 8,17,9 (faster) | ETH | 229 | 30.1% | -$1,641 | -1.15 | 0.80 | -$7.17 |
| 8,17,9 (faster) | HYPE | 222 | 27.5% | -$2,189 | -2.18 | 0.68 | -$9.86 |
| 12,26,9 (shipped) | BTC | 173 | 31.2% | -$893 | -0.61 | 0.88 | -$5.16 |
| 12,26,9 (shipped) | ETH | 168 | 27.4% | -$2,375 | -1.97 | 0.64 | -$14.14 |
| 12,26,9 (shipped) | HYPE | 163 | 29.4% | -$465 | -0.20 | 0.93 | -$2.85 |
| 19,39,9 (slower) | BTC | 136 | 25.7% | -$1,574 | -1.32 | 0.74 | -$11.57 |
| 19,39,9 (slower) | ETH | 144 | 29.2% | -$1,512 | -1.11 | 0.77 | -$10.50 |
| 19,39,9 (slower) | HYPE | 128 | 38.3% | +$1,070 | +1.16 | 1.20 | +$8.36 |

## One-line verdict

- **8,17,9:** combined -$6,752 on 689 trades -- the faster
  MACD churns more and loses more on every coin.
- **12,26,9:** the shipped setting -- combined -$3,733 on
  504 trades.
- **19,39,9:** combined -$2,015 on 408 trades -- the least
  bad, carried by HYPE (+$1,070, the only positive
  coin/parameter cell in the sweep) while BTC and ETH still
  lose over -$1,500 each.
- **Shipped decision:** keep MACD(12, 26, 9) as the registry
  config regardless. It was fixed before any backtest was
  run; the sweep is diagnostic only. The slower setting's
  smaller loss is not a win -- it is still negative combined,
  still loses on 2 of 3 coins, and its HYPE cell is a
  thin-sample outlier (128 trades, PF 1.20). Switching to
  (19, 39) on the strength of this sweep would be tuning to
  PnL. Do not ship a different parameter set.

## Audit

- **Lookahead audit:** no lookahead found. Both MACDs are
  causal EMA constructions; the 4h mapping is a backward
  as-of join on completed 4h bars only (see
  `strategies/timeframes.py`); ATR(14) is Wilder smoothing;
  signals use only bar-i values. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the Triple Screen construction (trade
  the fast timeframe's trigger only in the direction of the
  slow timeframe's trend) matches the cited Quantpedia
  article. One documented adaptation: the source's slow
  timeframe is the weekly trend on daily bars; here it is the
  4h trend on 1h bars, the same principle at intraday
  resolution, because the backtest grid is 1h.
- **Tests:** 17/17 pass (`python3 -m unittest
  strategies.mtf_macd_confirmation.test_mtf_macd_confirmation`).
- **No parameter was tuned to PnL.** MACD stays (12, 26, 9).
