# Williams %R Divergence — Calibration

%R-period sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-47 window
2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC, 6,160 bars
BTC/ETH, 6,158 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 120-bar max hold). The %R period is the strategy's
natural knob: 10 is the faster oscillator, 14 the standard,
21 the slowest. The sweep re-runs `add_indicators(df,
wr_n=X)` — the ±2-bar pivots, the −80/−20 divergence gates
and the −50 exit stay fixed throughout.

| %R period | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 49 | 32.7% | -$890 | -1.59 | 0.54 | -$18.15 |
| 10 | ETH | 46 | 32.6% | -$858 | -1.81 | 0.50 | -$18.64 |
| 10 | HYPE | 61 | 32.8% | -$1,411 | -2.74 | 0.39 | -$23.14 |
| 14 (shipped) | BTC | 59 | 20.3% | -$1,693 | -2.86 | 0.36 | -$28.70 |
| 14 (shipped) | ETH | 63 | 30.2% | -$1,593 | -2.91 | 0.36 | -$25.29 |
| 14 (shipped) | HYPE | 67 | 29.9% | -$1,483 | -2.28 | 0.50 | -$22.13 |
| 21 | BTC | 57 | 35.1% | -$905 | -1.16 | 0.67 | -$15.88 |
| 21 | ETH | 68 | 41.2% | -$611 | -0.54 | 0.78 | -$8.99 |
| 21 | HYPE | 72 | 33.3% | -$490 | -0.54 | 0.85 | -$6.80 |

## One-line verdict

- **10:** combined -$3,159 on 156 trades — fewer trades
  than shipped and a smaller loss, but still negative on
  every coin (PF 0.39–0.54).
- **14:** the shipped setting — combined -$4,769 on 189
  trades; the worst combined read and the worst BTC win
  rate in the sweep (20.3%).
- **21:** combined -$2,006 on 197 trades — the least-bad
  read (best win rates, 33–41%, and PF up to 0.85), but
  still negative on every coin.
- **Shipped decision:** keep the specified %R period = 14
  as the registry config regardless. It was fixed before
  any backtest was run; the sweep is diagnostic only. The
  21-bar read being "least bad" is in-sample information
  about a still-losing setting, not evidence to ship it —
  all three settings lose on all three coins, and the
  ranking flips between coins (10 beats 21 on HYPE, 21
  beats 10 on BTC/ETH), so the knob is not stable. Do not
  ship a different period on the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. %R(14) is a
  causal rolling range; confirmed pivots use only data
  through the confirmation bar (pivot bar i−2, confirmed
  at bar i); divergence compares the current pivot against
  the previous confirmed pivot; exits read bar i's %R vs
  bar i−1; no `ichimoku` chikou column is used anywhere.
  The truncation test (`test_no_lookahead_truncation`)
  confirms indicator, pivot/divergence and signal values at
  bar j are identical whether computed on the full frame or
  on the frame truncated at j.
- **Source check:** the %R formula and the divergence
  method (lower low / higher oscillator, oversold gate) are
  the standard Larry Williams %R divergence as cited in the
  README. One documented choice: the pivot machinery
  (±2-bar confirmed pivots, confirmation bar = pivot + 2)
  is taken exactly from strategies/macd_rsi_divergence, as
  specified in the build brief; the flat-range %R = −50
  convention is documented in indicators.py.
- **Tests:** 18/18 pass (`python3 -m unittest
  strategies.williams_r_divergence.test_williams_r_divergence`).
- **No parameter was tuned to PnL.** %R period stays 14.
