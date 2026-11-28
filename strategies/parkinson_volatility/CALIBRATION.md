# Parkinson Volatility Expansion — Calibration

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
| 10 bars | BTC | 193 | 36.3% | -$2,085 | -1.75 | 0.71 | -$10.80 |
| 10 bars | ETH | 216 | 30.1% | -$3,046 | -2.70 | 0.60 | -$14.10 |
| 10 bars | HYPE | 224 | 36.2% | -$1,370 | -1.09 | 0.81 | -$6.12 |
| 10 bars | **Combined** | **633** | **34.1%** | **-$6,501** | — | **0.70** | **-$10.27** |
| 20 bars (shipped) | BTC | 129 | 32.6% | -$1,217 | -1.10 | 0.76 | -$9.44 |
| 20 bars (shipped) | ETH | 149 | 33.6% | -$1,122 | -0.98 | 0.79 | -$7.53 |
| 20 bars (shipped) | HYPE | 146 | 38.4% | +$1,734 | 1.45 | 1.35 | +$11.87 |
| 20 bars (shipped) | **Combined** | **424** | **34.9%** | **-$606** | **-0.16** | **0.96** | **-$1.43** |
| 40 bars | BTC | 89 | 34.8% | +$545 | 0.59 | 1.15 | +$6.12 |
| 40 bars | ETH | 86 | 22.1% | -$2,023 | -2.69 | 0.50 | -$23.52 |
| 40 bars | HYPE | 97 | 36.1% | +$282 | 0.39 | 1.09 | +$2.91 |
| 40 bars | **Combined** | **272** | **31.2%** | **-$1,197** | — | **0.89** | **-$4.40** |

## Vol-SMA length (vol window fixed at 20)

| Vol SMA | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 30 bars | BTC | 163 | 31.3% | -$3,402 | -3.62 | 0.46 | -$20.87 |
| 30 bars | ETH | 171 | 29.2% | -$2,052 | -1.90 | 0.68 | -$12.00 |
| 30 bars | HYPE | 175 | 37.7% | -$374 | -0.22 | 0.94 | -$2.14 |
| 30 bars | **Combined** | **509** | **32.8%** | **-$5,828** | — | **0.69** | **-$11.45** |
| 60 bars (shipped) | **Combined** | **424** | **34.9%** | **-$606** | **-0.16** | **0.96** | **-$1.43** |
| 120 bars | BTC | 141 | 34.8% | -$335 | -0.22 | 0.93 | -$2.38 |
| 120 bars | ETH | 115 | 31.3% | -$27 | 0.06 | 0.99 | -$0.23 |
| 120 bars | HYPE | 132 | 38.6% | +$488 | 0.62 | 1.11 | +$3.70 |
| 120 bars | **Combined** | **388** | **35.1%** | **+$127** | — | **1.01** | **+$0.33** |

## One-line verdict

- **Vol window 10:** combined -$6,501 on 633 trades -- the
  fastest vol estimate churns hardest and loses most; a
  shorter window just admits more false expansions.
- **Vol window 20:** the shipped setting -- combined -$606
  on 424 trades.
- **Vol window 40:** combined -$1,197 on 272 trades -- fewer
  trades, still a loser; BTC and HYPE turn positive but ETH
  (-$2,023, win 22.1%) more than offsets them.
- **Vol SMA 30:** combined -$5,828 on 509 trades -- a
  faster baseline whipsaws the cross and multiplies the loss
  tenfold.
- **Vol SMA 60:** the shipped setting -- combined -$606
  on 424 trades.
- **Vol SMA 120:** combined +$127 on 388 trades -- the only
  positive variant, and it is a rounding error: PF 1.01,
  expectancy +$0.33/trade, no coin strongly positive. A
  slower baseline filters out marginal expansions, but
  +$127 on $30k over 8.4 months is breakeven, not an edge.
- **Shipped decision:** keep vol window = 20 and vol SMA =
  60 as the registry config regardless. Both were fixed
  before any backtest was run; the sweeps are diagnostic
  only. The +$127 vol-SMA-120 variant is not a reason to
  re-parameterize -- it is within noise of zero. Do not
  ship a different window or SMA length on the strength of
  this sweep.

## Audit

- **Lookahead audit:** no lookahead found. The Parkinson
  variance is a per-bar function of that bar's high/low
  only; pk_vol is a causal 20-bar rolling mean; the SMA
  and EMA are causal; entries are crossed_above on pk_vol
  vs its SMA. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the Parkinson estimator (ln(H/L)^2 /
  (4 ln2), 20-bar average, square root) matches the cited
  Parkinson reference. Two documented choices: the EMA(20)
  trend gate is a same-bar level test rather than a fresh
  cross, and a vol contraction exits both sides.
- **Tests:** 16/16 pass (`python3 -m unittest
  strategies.parkinson_volatility.test_parkinson_volatility`).
- **No parameter was tuned to PnL.** Vol window stays 20,
  vol SMA stays 60.
