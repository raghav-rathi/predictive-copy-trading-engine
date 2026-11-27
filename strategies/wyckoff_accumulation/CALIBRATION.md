# Wyckoff Accumulation — Calibration

Spring-reclaim and SOS-window sensitivity on the same
Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE, pinned
batch-48 window 2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC,
6,184 bars BTC/ETH, 6,182 HYPE; same costs/sizing, 2xATR
stop, 3xATR trail, 240-bar max hold, long only). The sweeps
re-run `add_indicators(df, spring_reclaim_bars=X)` /
`add_indicators(df, sos_window=X)` -- everything else stays
fixed.

## Spring reclaim window (SOS window fixed at 48 bars)

| Reclaim | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 2 bars | BTC | 25 | 20.0% | -$1,069 | -2.18 | 0.27 | -$42.75 |
| 2 bars | ETH | 26 | 26.9% | -$627 | -1.03 | 0.64 | -$24.11 |
| 2 bars | HYPE | 69 | 21.7% | -$1,278 | -1.47 | 0.63 | -$18.52 |
| 2 bars | **Combined** | **120** | **22.5%** | **-$2,974** | — | **0.55** | — |
| 3 bars (shipped) | BTC | 24 | 20.8% | -$1,019 | -2.09 | 0.28 | -$42.48 |
| 3 bars (shipped) | ETH | 23 | 30.4% | -$383 | -0.63 | 0.74 | -$16.64 |
| 3 bars (shipped) | HYPE | 71 | 25.4% | -$596 | -0.60 | 0.83 | -$8.39 |
| 3 bars (shipped) | **Combined** | **118** | **25.4%** | **-$1,998** | **-1.44** | **0.69** | **-$16.93** |
| 5 bars | BTC | 24 | 20.8% | -$1,019 | -2.09 | 0.28 | -$42.48 |
| 5 bars | ETH | 23 | 30.4% | -$383 | -0.63 | 0.74 | -$16.64 |
| 5 bars | HYPE | 72 | 25.0% | -$1,213 | -1.40 | 0.65 | -$16.84 |
| 5 bars | **Combined** | **119** | **25.2%** | **-$2,615** | — | **0.59** | — |

## SOS window (reclaim fixed at 3 bars)

| SOS window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 24 bars | BTC | 23 | 21.7% | -$995 | -2.11 | 0.29 | -$43.27 |
| 24 bars | ETH | 23 | 30.4% | -$383 | -0.63 | 0.74 | -$16.64 |
| 24 bars | HYPE | 68 | 23.5% | -$1,104 | -1.25 | 0.68 | -$16.23 |
| 24 bars | **Combined** | **114** | **24.6%** | **-$2,482** | — | **0.61** | — |
| 48 bars (shipped) | **Combined** | **118** | **25.4%** | **-$1,998** | **-1.44** | **0.69** | **-$16.93** |
| 96 bars | BTC | 25 | 20.0% | -$1,120 | -2.28 | 0.26 | -$44.78 |
| 96 bars | ETH | 24 | 29.2% | -$487 | -0.81 | 0.69 | -$20.31 |
| 96 bars | HYPE | 74 | 25.7% | -$607 | -0.59 | 0.84 | -$8.20 |
| 96 bars | **Combined** | **123** | **25.2%** | **-$2,214** | — | **0.68** | — |

## One-line verdict

- **Reclaim 2:** combined -$2,974 on 120 trades -- tighter
  reclaim admits fewer springs and loses more.
- **Reclaim 3:** the shipped setting -- combined -$1,998
  on 118 trades, the least-bad variant.
- **Reclaim 5:** combined -$2,615 on 119 trades -- a
  longer reclaim window adds one HYPE trade and loses more.
- **SOS 24:** combined -$2,482 on 114 trades -- a shorter
  SOS window drops a few LPS entries and loses more.
- **SOS 96:** combined -$2,214 on 123 trades -- a longer
  SOS window adds a few late LPS entries and loses more.
- **Shipped decision:** keep spring reclaim = 3 bars and SOS
  window = 48 bars as the registry config regardless. Both
  were fixed before any backtest was run; the sweeps are
  diagnostic only. The knobs move the result by hundreds of
  dollars on ~120 trades, not by an edge appearing or
  disappearing -- the binding constraint is the stop, not
  these windows. Do not ship different windows on the
  strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. Range high/low
  are trailing 120-bar rolling extremes; the spring dip is
  judged against the prior bar's range low (a stored past
  value); ATR(14) is Wilder smoothing; vol-SMA(20) is a
  trailing mean; the spring/SOS/LPS state machine only reads
  bars up to the current one; exit levels are frozen at the
  entry bar. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the accumulation construction (decline,
  selling climax, spring, sign of strength, last point of
  support, range projection) matches the cited ChartGuys
  reference. Documented choices: the climax is recorded but
  does not gate entries; the dip is measured against the
  prior range low; SOS/LPS are first-bar-only per setup;
  exit levels freeze at entry.
- **Tests:** 17/17 pass (`python3 -m unittest
  strategies.wyckoff_accumulation.test_wyckoff_accumulation`).
- **No parameter was tuned to PnL.** Reclaim stays 3 bars,
  SOS window stays 48 bars.
