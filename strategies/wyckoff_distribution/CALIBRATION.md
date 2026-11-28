# Wyckoff Distribution — Calibration

UTAD-reclaim and range-window sensitivity on the same
Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE, pinned
batch-49 window 2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC,
6,185 bars BTC/ETH, 6,183 HYPE; same costs/sizing, 2xATR
stop, 3xATR trail, 120-bar max hold, short only). The sweeps
re-run `add_indicators(df, utad_reclaim_bars=X)` /
`add_indicators(df, range_n=X)` -- everything else stays
fixed. (With range_n=240 the columns keep their
range_high_120 / range_low_120 names but are computed over
240 bars; signals.py reads them as-is.)

## UTAD reclaim window (range fixed at 120 bars)

| Reclaim | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 3 bars (shipped) | BTC | 19 | 15.8% | -$472 | -1.08 | 0.56 | -$24.84 |
| 3 bars (shipped) | ETH | 24 | 29.2% | -$668 | -1.30 | 0.48 | -$27.82 |
| 3 bars (shipped) | HYPE | 47 | 29.8% | -$980 | -1.47 | 0.50 | -$20.86 |
| 3 bars (shipped) | **Combined** | **90** | **26.7%** | **-$2,120** | **-1.92** | **0.51** | **-$23.56** |
| 5 bars | BTC | 19 | 15.8% | -$449 | -0.95 | 0.57 | -$23.62 |
| 5 bars | ETH | 22 | 27.3% | -$779 | -1.60 | 0.40 | -$35.43 |
| 5 bars | HYPE | 44 | 29.5% | -$527 | -0.72 | 0.74 | -$11.97 |
| 5 bars | **Combined** | **85** | **25.9%** | **-$1,755** | — | **0.60** | — |

## Range window (reclaim fixed at 3 bars)

| Range | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 120 bars (shipped) | **Combined** | **90** | **26.7%** | **-$2,120** | **-1.92** | **0.51** | **-$23.56** |
| 240 bars | BTC | 19 | 31.6% | +$89 | 0.21 | 1.09 | $4.69 |
| 240 bars | ETH | 23 | 34.8% | -$309 | -0.51 | 0.74 | -$13.45 |
| 240 bars | HYPE | 42 | 28.6% | -$632 | -0.91 | 0.60 | -$15.04 |
| 240 bars | **Combined** | **84** | **31.0%** | **-$852** | — | **0.77** | — |

## One-line verdict

- **Reclaim 3:** the shipped setting -- combined -$2,120
  on 90 trades.
- **Reclaim 5:** combined -$1,755 on 85 trades -- a longer
  reclaim window admits a few late UTADs and loses less,
  still a loser.
- **Range 240:** combined -$852 on 84 trades -- a wider
  range admits fewer, cleaner UTADs and loses much less;
  BTC even flips to +$89 on 19 trades. Still a combined
  loser, and the BTC flip is 19 trades -- noise, not an edge.
- **Shipped decision:** keep UTAD reclaim = 3 bars and range
  = 120 bars as the registry config regardless. Both were
  fixed before any backtest was run; the sweeps are
  diagnostic only. The range-240 variant being less bad does
  not make 240 the shipped setting -- switching on the
  strength of one window's sweep would be tuning to PnL, and
  the variant still loses combined. Do not ship a different
  reclaim or range on the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. Range high/low
  are trailing 120-bar rolling extremes; the UTAD poke is
  judged against the prior bar's range high (a stored past
  value); ATR(14) is Wilder smoothing; vol-SMA(20) is a
  trailing mean; the UTAD/SOW/LPSY state machine only reads
  bars up to the current one; exit levels are frozen at the
  entry bar. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the distribution construction (advance,
  buying climax, UTAD, sign of weakness, last point of
  supply, range projection) is the bearish mirror of the
  accumulation construction in batch 48 and matches the cited
  Wyckoff reference. Documented choices: the climax is
  recorded but does not gate entries; the poke is measured
  against the prior range high; SOW/LPSY are first-bar-only
  per setup; exit levels freeze at entry.
- **Tests:** 17/17 pass (`python3 -m unittest
  strategies.wyckoff_distribution.test_wyckoff_distribution`).
- **No parameter was tuned to PnL.** Reclaim stays 3 bars,
  range stays 120 bars.
