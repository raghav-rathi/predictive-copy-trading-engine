# Traders Dynamic Index — Calibration

RSI-period sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-46 window
2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC, 6,136 bars
BTC/ETH, 6,134 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 60-bar max hold). The RSI period is the strategy's
natural knob: how fast the whole TDI panel reacts — 10 is
twitchy, 21 is slow. The sweep re-runs
`add_indicators(df, rsi_n=X)` only — signals and risk are
unchanged. (The 2/7/34 line lengths and the 1.6185 band
multiplier stay at their canonical values throughout.)

| RSI period | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 261 | 28.0% | -$2,547 | -2.45 | 0.67 | -$9.76 |
| 10 | ETH | 250 | 24.8% | -$2,340 | -2.06 | 0.69 | -$9.36 |
| 10 | HYPE | 248 | 30.2% | -$2,742 | -3.54 | 0.57 | -$11.06 |
| 13 (shipped) | BTC | 246 | 27.2% | -$3,133 | -3.43 | 0.56 | -$12.74 |
| 13 (shipped) | ETH | 241 | 26.1% | -$2,572 | -2.35 | 0.65 | -$10.67 |
| 13 (shipped) | HYPE | 220 | 32.7% | -$1,617 | -1.88 | 0.73 | -$7.35 |
| 21 | BTC | 240 | 25.4% | -$3,478 | -3.97 | 0.51 | -$14.49 |
| 21 | ETH | 236 | 29.2% | -$1,934 | -1.61 | 0.73 | -$8.19 |
| 21 | HYPE | 225 | 31.1% | -$2,233 | -2.59 | 0.64 | -$9.93 |

## One-line verdict

- **10:** combined -$7,629 (759 trades) — most trades, worst
  on HYPE (-$2,742, PF 0.57); faster RSI just crosses more.
- **13:** the shipped setting — combined -$7,322 (707
  trades), the least-bad combined read, by $307 over 10 and
  $323 over 21 — noise, not an edge.
- **21:** combined -$7,645 (701 trades) — best single-coin
  read in the sweep on ETH (-$1,934, PF 0.73) but worst on
  BTC (-$3,478, PF 0.51). The knob is unstable by coin.
- **Shipped decision:** keep the specified RSI(13) as the
  registry config regardless. It was fixed before any
  backtest was run; the sweep is flat (combined -$7,322 to
  -$7,645 across the whole range) and no value approaches
  breakeven, so there is nothing here to adopt — and adopting
  13 *because* it is least-bad in-sample would still be
  in-sample selection. The honest read: the cross-plus-filter
  logic loses at any RSI length.

## Batch-46 audit (2026-11-25)

- **Lookahead audit:** no lookahead found. Wilder RSI is a
  causal ewm; the 2/7/34 SMAs and the 34-bar rolling std use
  data through bar i only; signals use `crossed_above`/
  `crossed_below` on bars i and i−1 only, plus level
  comparisons on bar i only. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the Quantum Algo TDI guide (verified URL,
  given in the batch-46 brief) confirms RSI 13, the 2/7/34
  line lengths, the 1.6185 volatility-band multiplier, and
  the 50-level base-line filter. The implementation follows
  it as specified; the bands are stored but not used by the
  shipped signals, which is documented in the README.
- **Tests:** 15/15 pass (`python3 -m unittest
  strategies.tdi_traders_dynamic.test_tdi_traders_dynamic`).
  Note from test development: the base-line filter is slow
  enough that a clean V-shaped price series produces no
  entries at all (the cross fires while the price line is
  still below the base) — the trend tests therefore use
  drifting random walks, which fire longs-only in an
  uptrend and shorts-only in a downtrend. That is a property
  of the filter, not a test artefact.
- **No parameter was tuned to PnL.** RSI stays 13.
