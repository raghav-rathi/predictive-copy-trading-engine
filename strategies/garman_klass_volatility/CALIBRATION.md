# Garman-Klass Volatility Expansion — Calibration

Vol-window and vol-SMA sensitivity on the same Hyperliquid
1h data as BACKTEST.md (BTC/ETH/HYPE, pinned batch-49
window 2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC, 6,185
bars BTC/ETH, 6,183 HYPE; same costs/sizing, 2xATR stop,
3xATR trail, 72-bar max hold). The sweeps re-run
`add_indicators(df, vol_window=X)` / `add_indicators(df,
vol_sma=X)` -- everything else stays fixed.

## Vol window (vol SMA fixed at 60)

| Vol window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 bars | BTC | 201 | 32.3% | -$2,398 | -2.07 | 0.66 | -$11.93 |
| 10 bars | ETH | 220 | 29.5% | -$2,973 | -2.61 | 0.63 | -$13.51 |
| 10 bars | HYPE | 220 | 34.1% | -$1,174 | -0.89 | 0.84 | -$5.34 |
| 10 bars | **Combined** | **641** | **32.0%** | **-$6,544** | — | **0.71** | **-$10.21** |
| 20 bars (shipped) | BTC | 140 | 31.4% | -$821 | -0.70 | 0.84 | -$5.86 |
| 20 bars (shipped) | ETH | 144 | 31.9% | -$1,492 | -1.40 | 0.74 | -$10.36 |
| 20 bars (shipped) | HYPE | 140 | 37.9% | -$150 | -0.07 | 0.97 | -$1.07 |
| 20 bars (shipped) | **Combined** | **424** | **33.7%** | **-$2,463** | **-1.06** | **0.85** | **-$5.81** |
| 40 bars | BTC | 91 | 31.9% | +$419 | 0.47 | 1.12 | +$4.60 |
| 40 bars | ETH | 101 | 23.8% | -$2,171 | -2.87 | 0.51 | -$21.50 |
| 40 bars | HYPE | 90 | 37.8% | +$65 | 0.14 | 1.02 | +$0.72 |
| 40 bars | **Combined** | **282** | **30.9%** | **-$1,686** | — | **0.85** | **-$5.98** |

## Vol-SMA length (vol window fixed at 20)

| Vol SMA | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 30 bars | BTC | 169 | 34.9% | -$2,722 | -2.73 | 0.58 | -$16.11 |
| 30 bars | ETH | 176 | 31.8% | -$2,567 | -2.44 | 0.60 | -$14.59 |
| 30 bars | HYPE | 172 | 36.0% | -$628 | -0.53 | 0.89 | -$3.65 |
| 30 bars | **Combined** | **517** | **34.2%** | **-$5,917** | — | **0.68** | **-$11.44** |
| 60 bars (shipped) | **Combined** | **424** | **33.7%** | **-$2,463** | **-1.06** | **0.85** | **-$5.81** |
| 120 bars | BTC | 152 | 38.8% | +$596 | 0.57 | 1.12 | +$3.92 |
| 120 bars | ETH | 119 | 26.9% | -$1,496 | -1.62 | 0.68 | -$12.57 |
| 120 bars | HYPE | 116 | 37.9% | +$958 | 1.02 | 1.26 | +$8.26 |
| 120 bars | **Combined** | **387** | **34.9%** | **+$58** | — | **1.00** | **+$0.15** |

## One-line verdict

- **Vol window 10:** combined -$6,544 on 641 trades -- the
  fastest vol estimate churns hardest and loses most; a
  shorter window just admits more false expansions.
- **Vol window 20:** the shipped setting -- combined -$2,463
  on 424 trades.
- **Vol window 40:** combined -$1,686 on 282 trades -- the
  least-bad window, still a loser; BTC and HYPE turn
  positive but ETH (-$2,171, win 23.8%) more than offsets
  them.
- **Vol SMA 30:** combined -$5,917 on 517 trades -- a
  faster baseline whipsaws the cross and doubles the loss.
- **Vol SMA 60:** the shipped setting -- combined -$2,463
  on 424 trades.
- **Vol SMA 120:** combined +$58 on 387 trades -- the only
  positive variant, and it is a rounding error: PF 1.00,
  expectancy +$0.15/trade, ETH still -$1,496. A slower
  baseline filters out marginal expansions, but +$58 on
  $30k over 8.4 months is breakeven, not an edge.
- **Shipped decision:** keep vol window = 20 and vol SMA =
  60 as the registry config regardless. Both were fixed
  before any backtest was run; the sweeps are diagnostic
  only. The +$58 vol-SMA-120 variant is not a reason to
  re-parameterize -- it is within noise of zero and its
  per-coin results are still split. Do not ship a different
  window or SMA length on the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. The GK variance
  is a per-bar function of that bar's OHLC only; gk_vol is
  a causal 20-bar rolling mean; the SMA and EMA are causal;
  entries are crossed_above on gk_vol vs its SMA. The
  truncation test (`test_no_lookahead_truncation`) confirms
  indicator and signal values at bar j are identical
  whether computed on the full frame or on the frame
  truncated at j.
- **Source check:** the GK estimator (0.5*ln(H/L)^2 -
  (2 ln2 - 1)*ln(C/O)^2, per-bar clip at zero, 20-bar
  average, square root) matches the cited Garman-Klass
  reference. Two documented choices: the EMA(20) trend
  gate is a same-bar level test rather than a fresh cross,
  and a vol contraction exits both sides.
- **Tests:** 17/17 pass (`python3 -m unittest
  strategies.garman_klass_volatility.test_garman_klass_volatility`).
- **No parameter was tuned to PnL.** Vol window stays 20,
  vol SMA stays 60.
