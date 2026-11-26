# Dynamic Momentum Index — Calibration

Base-period sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-47 window
2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC, 6,160 bars
BTC/ETH, 6,158 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 120-bar max hold). The base period is the strategy's
natural knob: it sets TD = clamp(int(base/Vi), 5, 30), so 10
is the fastest DMI, 14 the published standard, 21 the
slowest. The sweep re-runs `add_indicators(df,
base_period=X)` — the 30/70 entry and 50 exit levels stay
fixed throughout.

| Base period | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 401 | 34.9% | -$5,715 | -5.04 | 0.50 | -$14.25 |
| 10 | ETH | 384 | 37.0% | -$2,468 | -1.40 | 0.80 | -$6.43 |
| 10 | HYPE | 395 | 42.3% | -$2,008 | -1.13 | 0.84 | -$5.08 |
| 14 (shipped) | BTC | 347 | 36.3% | -$5,541 | -5.06 | 0.49 | -$15.97 |
| 14 (shipped) | ETH | 336 | 43.5% | -$2,207 | -1.46 | 0.82 | -$6.57 |
| 14 (shipped) | HYPE | 336 | 45.5% | -$2,124 | -1.31 | 0.81 | -$6.32 |
| 21 | BTC | 259 | 42.5% | -$3,676 | -3.02 | 0.60 | -$14.19 |
| 21 | ETH | 258 | 44.2% | -$357 | -0.13 | 0.97 | -$1.38 |
| 21 | HYPE | 240 | 42.1% | -$1,880 | -1.43 | 0.81 | -$7.83 |

## One-line verdict

- **10:** combined -$10,191 on 1,180 trades — the fastest
  DMI trades the most and loses the most; BTC worsens to
  -$5,715.
- **14:** the shipped setting — combined -$9,873 on 1,019
  trades; negative on every coin (PF 0.49–0.82).
- **21:** combined -$5,912 on 757 trades — the least-bad
  read (ETH nearly flat at -$357, PF 0.97), but still
  negative on every coin and still a loser overall.
- **Shipped decision:** keep the specified base period =
  14 as the registry config regardless. It was fixed before
  any backtest was run; the sweep is diagnostic only. The
  21-bar read being "least bad" is in-sample information
  about a still-losing setting, not evidence to ship it —
  all three settings lose on all three coins, so the knob
  is not stable, it is just three shades of negative. Do
  not ship a different base period on the strength of this
  sweep.

## Audit

- **Lookahead audit:** no lookahead found. sd5 / sd_avg /
  Vi / TD are causal rolling quantities; the DMI at bar i
  uses only closes through bar i; signals compare DMI
  against fixed levels via crossed_above / crossed_below
  (bar i vs bar i-1); no `ichimoku` chikou column is used
  anywhere. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the formula (sd5, SMA(sd5, 10), Vi,
  TD = clamp(int(14/Vi), 5, 30), RSI over TD changes) and
  the 30/70/50 levels are Chande & Kroll as cited in the
  README (LuxAlgo concept page and Wickra indicator docs).
  One documented deviation: the RSI is the definitional
  simple-mean form, NOT Wilder smoothing — Wilder over a
  changing window has no canonical definition, and the
  choice is stated in indicators.py and README.md.
- **Tests:** 16/16 pass (`python3 -m unittest
  strategies.dynamic_momentum_index.test_dynamic_momentum_index`).
- **No parameter was tuned to PnL.** Base period stays 14.
