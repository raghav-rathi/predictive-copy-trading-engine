# Day-of-Week Effect (Bitcoin) — Calibration

Leg-combination sensitivity on the same Hyperliquid 1h data
as BACKTEST.md (BTC/ETH/HYPE, pinned batch-49 window
2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC, 6,185 bars
BTC/ETH, 6,183 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 30-bar max hold). The sweeps re-run
`add_signals(df, ...)` -- everything else stays fixed.
The shipped config was fixed from the literature before
any backtest was run; these variants are diagnostic only.

## Leg combinations

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| Mon long + Thu short (shipped) | BTC | 73 | 39.7% | +$739 | 0.75 | 1.20 | +$10.12 |
| Mon long + Thu short (shipped) | ETH | 73 | 52.1% | +$2,877 | 2.36 | 1.87 | +$39.42 |
| Mon long + Thu short (shipped) | HYPE | 73 | 39.7% | +$1,448 | 1.48 | 1.40 | +$19.83 |
| Mon long + Thu short (shipped) | **Combined** | **219** | **43.8%** | **+$5,064** | **1.80** | **1.48** | **+$23.12** |
| Mon long only | BTC | 36 | 36.1% | -$167 | -0.18 | 0.91 | -$4.64 |
| Mon long only | ETH | 36 | 47.2% | +$1,062 | 1.30 | 1.69 | +$29.50 |
| Mon long only | HYPE | 36 | 30.6% | +$317 | 0.49 | 1.17 | +$8.81 |
| Mon long only | **Combined** | **108** | **38.0%** | **+$1,213** | — | — | **+$11.23** |
| Mon + Wed long + Thu short | BTC | 110 | 39.1% | -$380 | -0.23 | 0.93 | -$3.45 |
| Mon + Wed long + Thu short | ETH | 110 | 49.1% | +$3,360 | 2.13 | 1.61 | +$30.55 |
| Mon + Wed long + Thu short | HYPE | 110 | 35.5% | +$1,930 | 1.41 | 1.31 | +$17.55 |
| Mon + Wed long + Thu short | **Combined** | **330** | **41.2%** | **+$4,911** | — | — | **+$14.88** |

## One-line verdict

- **Mon long + Thu short (shipped):** combined +$5,064 on
  219 trades -- the best variant, and the one fixed from
  the literature.
- **Mon long only:** combined +$1,213 on 108 trades -- the
  Monday leg alone is worth roughly a quarter of the
  shipped total; the Thursday short carries the result.
  (Small differences vs the per-leg attribution in
  BACKTEST.md are the sizing path: in the standalone run
  the equity path -- and therefore 1%-risk sizing --
  evolves without the short legs.)
- **Mon + Wed long + Thu short:** combined +$4,911 on 330
  trades -- 111 more trades for $153 LESS profit. The
  Wednesday long adds churn, not edge (BTC goes negative
  in this variant), and its exit shares the Wednesday
  23:00 bar with the Thursday short entry.
- **Shipped decision:** keep Mon long + Thu short as the
  registry config regardless. The variants were not tuned
  toward -- the shipped config happens to be best, but by
  a margin ($153 over the Wed variant) that is noise, and
  the honest conclusion is that only the Thursday short
  leg is doing real work in this window. Do not ship a
  different leg combination on the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. Weekday/hour
  come only from each bar's own timestamp; ATR(14) is
  Wilder smoothing; each signal fires on exactly one
  weekday+hour bar per week. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the legs (long Monday, short Thursday)
  match the cited literature -- Monday strength (Decourt
  et al. 2017; Caporale & Plastun 2018) and Thursday as
  the weakest weekday in 2017-2026 Binance daily data
  (FairHatch 2026). The literature is mixed on whether the
  effect persists out of sample; the BACKTEST.md verdict
  says so plainly.
- **Tests:** 14/14 pass (`python3 -m unittest
  strategies.day_of_week_effect.test_day_of_week_effect`).
- **No parameter was tuned to PnL.** The legs are fixed
  from the literature.
