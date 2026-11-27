# Alligator + Awesome Oscillator Combo — Calibration

Fractal-window sensitivity on the same Hyperliquid 1h data
as BACKTEST.md (BTC/ETH/HYPE, pinned batch-48 window
2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC, 6,184 bars
BTC/ETH, 6,182 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 120-bar max hold). The fractal window is the
strategy's natural knob: 1 bar confirms faster (less lag,
more noise), 2 bars is the canonical Bill Williams setting
and the shipped one, 3 bars is stricter (fewer, cleaner
fractals). The sweep re-runs `add_indicators(df, frac_n=X)`
-- everything else (Alligator 13/8/5, AO 5/34, entry/exit
rules) stays fixed.

| Fractal window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 1 | BTC | 240 | 29.6% | -$3,126 | -2.69 | 0.63 | -$13.03 |
| 1 | ETH | 255 | 29.0% | -$2,501 | -1.87 | 0.72 | -$9.81 |
| 1 | HYPE | 260 | 30.8% | -$2,178 | -1.96 | 0.75 | -$8.38 |
| 2 (shipped) | BTC | 223 | 29.6% | -$3,081 | -2.72 | 0.63 | -$13.82 |
| 2 (shipped) | ETH | 231 | 27.7% | -$2,708 | -2.15 | 0.68 | -$11.72 |
| 2 (shipped) | HYPE | 224 | 32.6% | -$1,525 | -1.39 | 0.80 | -$6.81 |
| 3 | BTC | 214 | 30.4% | -$2,740 | -2.41 | 0.65 | -$12.80 |
| 3 | ETH | 213 | 31.5% | -$758 | -0.42 | 0.91 | -$3.56 |
| 3 | HYPE | 219 | 32.9% | -$1,563 | -1.48 | 0.79 | -$7.14 |

## One-line verdict

- **1 bar:** combined -$7,805 on 755 trades -- fastest
  confirmation, most trades, worst result.
- **2 bars:** the shipped setting -- combined -$7,314 on
  678 trades.
- **3 bars:** combined -$5,061 on 646 trades -- least-bad
  (ETH improves sharply to -$758, PF 0.91), but still a
  loser on every coin.
- **Shipped decision:** keep the canonical fractal window
  = 2 as the registry config regardless. It was fixed
  before any backtest was run; the sweep is diagnostic
  only. The 3-bar setting being least-bad is not a rescue
  -- it still loses $5,061 across 646 trades, and picking
  it on the strength of one window (driven mostly by ETH)
  would be tuning to PnL. Do not ship a different window
  on the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. SMMA/SMA are
  causal recursions; fractals are confirmed with a 2-bar
  lag (the column is set at bar i+2, never earlier); the
  forward-filled fractal level only ever carries a past
  confirmed extreme, and the level-stability guard blocks
  crosses against a level that just changed; no shifted
  (forward-displaced) Alligator values are used anywhere.
  The truncation test (`test_no_lookahead_truncation`)
  confirms indicator and signal values at bar j are
  identical whether computed on the full frame or on the
  frame truncated at j.
- **Source check:** the construction (Alligator SMMA
  13/8/5 of median price, AO SMA(5)-SMA(34), 2-bar
  fractals, fractal-breakout entry with AO and mouth
  filters) matches the cited Profitunity reference. One
  documented deviation: the book's 8/5/3-bar forward
  displacement of the Alligator lines is not used --
  unshifted SMMA values, since shifted values would be
  lookahead.
- **Tests:** 16/16 pass (`python3 -m unittest
  strategies.alligator_awesome_combo.test_alligator_awesome_combo`).
- **No parameter was tuned to PnL.** Fractal window stays 2.
